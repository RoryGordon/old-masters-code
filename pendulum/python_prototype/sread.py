import time
import serial

import numpy as np
from cobs import cobs


COMPORT = 'COM4'
#start_time = time.time()

'''

PLOT theta_ddot against sin(theta)

'''

class Sensor():
    def __init__(self):
        self.radius = 0.4  # for calculating theta_ddot from y_acc
        #
        # Open the USB port
        #
        print('Wait a few seconds for serial port to open...')
        try:
            self.ser = serial.Serial(COMPORT, baudrate=9600)  # 57600
            self.ser.isOpen()  # try to open the port; will cause error if port is already open
        except IOError:  # if the port is already open, close it and open it again
            self.ser.close()
            self.ser.open()

        time.sleep(2)  # pause for 2 seconds to allow port to settle down
        self.ser.flush()    # flush the port to remove any spurious data
        # print name of port to confirm correct opening
        print('Serial port open:', self.ser.name)

        # Execute the readmotiondata function once to read the first (possibly incomplete) line of bytes and ignore it
        self.readmotiondata()

        # read sufficient number of lines from serial port to flush buffer before recording/plotting
        
        for x in range(150):
            self.readmotiondata()
        
        #self.start_time = self.update()[0]

    def readmotiondata(self):

        eol = bytes([0])  # define the end of line character as a zero byte
        motiond = bytearray()  # set up an array of bytes
        # self.ser.flush()
        while True:
            c = self.ser.read()  # read a byte from the serial port into variable c
            if c == eol:
                break    # if the end of line character is read, return from the function with the bytes in motiond
            else:
                motiond += c  # otherwise append the byte to the array
        return bytes(motiond)

    def update(self):
        # serial read into bytes object converted to list of ints, last element is line feed
        motioncoded = self.readmotiondata()

        try:
            motiondata = cobs.decode(motioncoded)  # cobs
        except cobs.DecodeError:
            print('COBS DecodeError')
            print(f"     {motioncoded}")
        else:

            # bytes object converted to list of ints, last element is line feed
            data_list = list(motiondata)

            checksumrecvd = np.sum(data_list[0:24], dtype=np.uint8)  # checksum

            if (checksumrecvd != data_list[-1]):
                print(f'Checksum error: {checksumrecvd} != {data_list[-1]}')
                print(f"    {data_list}")
                return None

            else:
                millis = np.uint32(
                    motiondata[0] | motiondata[1] << 8 | motiondata[2] << 16 | motiondata[3] << 24)
                accx = np.int16(motiondata[4] | motiondata[5] << 8)
                accy = np.int16(motiondata[6] | motiondata[7] << 8)
                gyrz = np.int16(motiondata[20] | motiondata[21] << 8)
                # 22 = 4 time bytes + 18 imu bytes
                encoder = np.int16(motiondata[22] | motiondata[23] << 8)

            return (millis, accx, accy, gyrz, encoder)

    def get_val(self):
        self.ser.flush()
        self.readmotiondata()
        return self.update()


class IMU(Sensor):
    def __init__(self):
        super().__init__()

    def update(self):
        # serial read into bytes object converted to list of ints, last element is line feed
        motioncoded = self.readmotiondata()

        try:
            motiondata = cobs.decode(motioncoded)  # cobs
        except cobs.DecodeError:
            print('COBS DecodeError')
            print(f"     {motioncoded}")
        else:

            # bytes object converted to list of ints, last element is line feed
            data_list = list(motiondata)

            checksumrecvd = np.sum(data_list[0:-1], dtype=np.uint8)  # checksum

            if (checksumrecvd != data_list[-1]):
                print(f'Checksum error: {checksumrecvd} != {data_list[-1]}')
                print(f"    {data_list}")
                return None

            else:
                millis = np.uint32(
                    motiondata[0] | motiondata[1] << 8 | motiondata[2] << 16 | motiondata[3] << 24)
                accy = np.int16(motiondata[4] | motiondata[5] << 8)
                gyrz = np.int16(motiondata[6] | motiondata[7] << 8)
                gx = np.int16(motiondata[8] | motiondata[9] << 8)
                gy = np.int16(motiondata[10] | motiondata[11] << 8)

                magnitude = np.sqrt(gx**2 + gy**2)
                angle = np.arcsin(gy/magnitude)
                if gx < 0:
                    if gy < 0:
                        angle = -np.pi - angle
                    else:
                        angle = np.pi - angle
                anglebyte = np.int16(-angle*900) # 1 radian = 900 LSB

            return (millis, accy, gyrz, gx, gy, anglebyte)


if __name__ == '__main__':
    sensor = IMU()
    while True:
        data = sensor.update()
        if data is not None:
            print(f"{data[3]/100:5.4f}, {data[4]/100:5.4f} | "
                  f"angle = {data[5]}")
            '''
            x_dots = int(np.floor((data[1]+1024)/16))
            y_dots = int(np.floor((data[2]+1024)/16))
            spaces = 128-x_dots
            string = '.'*x_dots + ' '*spaces + '.'*y_dots
            print(string)
            '''
