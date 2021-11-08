import time
import serial

from typing import List
from cobs import cobs

import numpy as np

import pygame

from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLU import *
RADIUS = 200

SCREEN_X = 2*RADIUS + 40
SCREEN_Y = 2*RADIUS + 40

COMPORT = 'COM4'
EOL = bytes([0])  # define the end of line character as a zero byte

class Model:
    def __init__(self):
        pass

class View:
    def __init__(self):
        pass

class Controller:
    def __init__(self):
        pass


class SerialInt:
    def __init__(self,
                 gX: int,
                 gY: int,
                 vXY: int,
                 aX: int,
                 aY: int):
        self.gX = gX
        self.gY = gY
        self.vXY = vXY
        self.aX = aX
        self.aY = aY


class SerialFloat:
    def __init__(self,
                 gX: float,
                 gY: float,
                 vXY: float,
                 aX: float,
                 aY: float):
        self.gX = gX
        self.gY = gY
        self.vXY = vXY
        self.aX = aX
        self.aY = aY


class Observables:
    def __init__(self,
                 theta: float,
                 thetaDot: float,
                 thetaDdot: float,
                 predHeight: float):
        self.theta = theta
        self.thetaDot = thetaDot
        self.thetaDdot = thetaDdot
        self.predHeight = predHeight


class View:
    def __init__(self):
        self._controller = Controller
        self._model = Model

        pygame.init()
        window_size = (SCREEN_X, SCREEN_Y)
        pygame.display.set_mode(
            window_size,
            flags=DOUBLEBUF | OPENGL
            )
        glOrtho(
            -SCREEN_X/2, SCREEN_X/2,
            -SCREEN_Y/2, SCREEN_Y/2, -1, 1
        )
    
    def setModel(self, model: Model):
        self._model = model
    
    def setController(self, controller: Controller):
        self._controller = controller
    
    def _check_quit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._controller.setIsRunning(False)
                None
        return None

    def _drawPendulum(self, theta: float) -> None:
        pass

    def _drawPredHeight(self, predHeight: float) -> None:
        pass

    def notify(self) -> None:
        modelState = self._model.getState()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self._drawPendulum(modelState.theta)
        self._drawPredHeight(modelState.predHeight)

        pygame.display.flip()


class Model:
    def __init__(self):
        self._view = View

        self._theta = 0
        self._thetaDot = 0
        self._thetaDdot = 0
        self._predHeight = 0

        self._oldTheta = 1
        self._oldThetaDot = 1

        self._bigC = 0
        self._deviceRadius = 0

        self._isCalibrating = False
        self._samples = 0
        self._apexSamples = 0
        self._baseSamples = 0
        self._cTMaxSum = 0
        self._tDSqMaxSum = 1
    
    def _thetaSignChange(self) -> float:
        return self._oldTheta * self._theta

    def _thetaDotSignChange(self) -> float:
        return self._oldThetaDot * self._thetaDot

    def getCalibState(self) -> bool:
        return self._isCalibrating

    def getState(self) -> Observables:
        print(
            f"{self._theta:7.3f} "
            f"| {self._thetaDot:7.3f} "
            f"| {self._thetaDdot:7.3f}"
        )
        return Observables(
            self._theta,
            self._thetaDot,
            self._thetaDdot,
            self._predHeight
        )

    def setView(self, view: View) -> None:
        self._view = view
        return None

    def update(self, serialIn: SerialFloat) -> None:
        self._oldTheta = self._theta
        self._oldThetaDot = self._thetaDot

        self._theta = self._setTheta(serialIn)
        self._thetaDot = serialIn.vXY
        self._thetaDdot = serialIn.aY / self._deviceRadius

        if self._bigC != None:
            self._predHeight = (
                np.cos(self._theta) - self._bigC*self._thetaDot**2
            )
        else:
            self._predHeight = None
        
        if self._isCalibrating:
            if self._thetaDotSignChange() <= 0:
                self._cTMaxSum += np.cos(self._theta)
                self._apexSamples += 1
                self._samples += 1
                if self._samples >= 10:
                    self._isCalibrating = False
                    self._apexSamples = 0
                    self._baseSamples = 0
                    self._samples = 0
            elif self._thetaSignChange() <= 0:
                self._deviceRadius = (
                    -serialIn.aX / self._thetaDot**2
                )
                self._baseSamples += 1
                self._samples += 1
                if self._samples >= 10:
                    self._isCalibrating = False
                    self._apexSamples = 0
                    self._baseSamples = 0
                    self._samples = 0
        
        self._view.notify()
        return None

    def zeroSet(self):
        pass

    def calibrate(self) -> None:
        self._isCalibrating = True

    def _setTheta(self, values: SerialFloat) -> float:
        theta = np.arctan(values.gY/values.gX)
        if values.gX< 0:
            if values.gY < 0:
                theta -= np.pi
            else:
                theta += np.pi

        return theta

    def _calculateBigC(self) -> None:
        bigCNew = float
        if self._tDSqMaxSum != 0 and self._apexSamples != 0:
            bigCNew = (
                (self._baseSamples / self._tDSqMaxSum)*
                (1- self._cTMaxSum / self._apexSamples)
            )
        else:
            bigCNew = 0.0
        self._bigC = bigCNew
        return None


class Controller:
    def __init__(self):
        self._model = Model()
        self._view = View()

        self.ser = serial.Serial(COMPORT, baudrate=9600)  # 57600

        self._model.setView(self._view)
        self._view.setModel(self._model)
        self._view.setController(self)

        self._isRunning = True

    def setup(self) -> None:
        try:
            self.ser.isOpen()
        except IOError:
            self.ser.close()
            self.ser.open()

        time.sleep(2)  # pause for 2 seconds to allow port to settle down
        self.ser.flush()    # flush the port to remove any spurious data
        # print name of port to confirm correct opening
        print('Serial port open:', self.ser.name)

        # Execute the readmotiondata function once to read the first (possibly incomplete) line of bytes and ignore it
        self._readBytes()

    def readSerial(self) -> None:
        codedBytes = self._readBytes()
        serialIn = self._decodeBytes(codedBytes)

        if serialIn != None:
            self._model.update(serialIn)
        return None

    def _readBytes(self) -> bytearray:
        motiond = bytearray()

        while True:
            c = self.ser.read()
            if c != EOL:
                motiond += c
            else:
                # print(bytes(motiond))
                return bytes(motiond)
    
    def _decodeBytes(self, codedBytes: bytearray) -> SerialFloat:
        try:
            decodedBytes = cobs.decode(codedBytes)
        except cobs.DecodeError:
            print("COBS DecodeError!")
            return None
        else:
            
            if self._verifyBytes(decodedBytes):
                millis = np.uint32(
                    decodedBytes[0] | decodedBytes[1] << 8 | 
                    decodedBytes[2] << 16 | decodedBytes[3] << 24
                )
                aX = np.int16(0)
                aY = np.int16(
                    decodedBytes[4] | decodedBytes[5] << 8
                )
                vXY = np.int16(
                    decodedBytes[6] | decodedBytes[7] << 8
                )
                gX = np.int16(
                    decodedBytes[8] | decodedBytes[9] << 8
                )
                gY = np.int16(
                    decodedBytes[10] | decodedBytes[11] << 8
                )
                return self._serialToFloat(
                    SerialInt(gX, gY, vXY, aX, aY)
                )

    def _verifyBytes(self, decodedBytes: bytearray) -> bool:
        decodedList = list(decodedBytes)
        checksum = np.sum(decodedList[0:24], dtype=np.uint8)
        return True
        if checksum == decodedList[-1]:
            return True
        else:
            print(f"Checksum Failed! {checksum} : {decodedList[-1]}")
            return False

    def _serialToFloat(self, serialIn: SerialInt) -> SerialFloat:
        gXf = serialIn.gX / 100
        gYf = serialIn.gY / 100
        vXYf = serialIn.vXY / 900
        aXf = serialIn.aX / 100
        aYf = serialIn.aY / 100
        return SerialFloat(gXf, gYf, vXYf, aXf, aYf)

    def setIsRunning(self, isRunning: bool) -> None:
        self._isRunning = isRunning
        return None

    def main(self) -> None:
        self.setup()
        while self._isRunning:
            self.readSerial()

if __name__ == "__main__":
    c = Controller()
    c.main()