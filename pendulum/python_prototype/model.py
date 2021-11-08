import numpy as np
from sread import IMU

GRAVITY = 9.81
Z_CONV = 900  # according to adafruit.py


class Pendulum:
    def __init__(self):
        self.sensor = IMU()
        # in metres (is really 0.05 but we'll change that later)
        self.length = .05
        self.sensor_radius = 0.4
        self.mass = 1.35  # in kg, and a complete guess
        self.j = 0.1402  # another poorly educated guess

        #self.acc_y = 0

        #self.theta = 0  # -gyr_offset
        self.int_theta = 0
        #self.theta_dot = 0
        #self.theta_ddot = 0
        self.theta_ddot_diff = 0

        self.state = State()
        self.prev_state = State()

        #self.prev_time = 0
        #self.prev_acc_y = 0
        #self.prev_theta_dot = 0
        self.prev_swing_z_sign = 1
        self.prev_swing_t_dd_sign = 1
        self.prev_peak = 0

        self.swing_count = 0

        self.pred_height = 0
        self.height_list = []
        self.j_list = []
        self.ddot_error = []

        self.print_counter = 0

    def __check_0_crossing_t_dd(self):
        theta_ddot_sign_change = ((np.floor(self.prev_acc_y) + 0.5) *
                                  (np.floor(self.acc_y) + 0.5))

        theta_dot_sign_change = self.prev_swing_z_sign * self.state.theta_dot
        if theta_ddot_sign_change <= 0 and theta_dot_sign_change <= 0:
            if self.prev_swing_z_sign == 1:
                self.swing_count += 1
                self.prev_swing_z_sign = -1
            else:
                self.prev_swing_z_sign = 1
            return True
        else:
            return False

    def __check_0_crossing_t_d(self):
        theta_dot_sign_change = ((np.floor(self.prev_state.theta_dot) + 0.5) *
                                 (np.floor(self.state.theta_dot) + 0.5))

        theta_ddot_sign_change = self.prev_swing_t_dd_sign * self.state.theta_ddot
        if theta_ddot_sign_change <= 0 and theta_dot_sign_change <= 0:
            if self.prev_swing_t_dd_sign == 1:
                self.prev_swing_t_dd_sign = -1
            else:
                self.prev_swing_t_dd_sign = 1
            return True
        else:
            return False

    def update(self):
        data = self.sensor.update()
        if data is not None:
            self.state.time = data[0]/1000  # From ms into s
            self.acc_y = data[1]/100
            self.state.theta_dot = data[2]/Z_CONV
            self.g_y = data[4]/100
            self.state.theta = data[5]/Z_CONV

            '''
            if self.print_counter == 0:
                a = self.acc_y
                b = self.g_y
                print(f"\n"
                    f"Data:\n    {a}\n"
                    f"Gravity:\n    {b}\n"
                    f"Result:\n {a-b}")
            '''

            self.state.theta_ddot = -(self.acc_y - self.g_y)/self.sensor_radius

            dt = self.state.time - self.prev_state.time
            self.theta_ddot_diff = (self.state.theta_dot-self.prev_state.theta_dot)/dt

            if self.__check_0_crossing_t_dd():
                self.int_theta = 0  # if theta_ddot changes sign, theta should be 0
                energy = 0.5 * (self.j + self.length**2) * self.state.theta_dot**2
                self.pred_height = energy / GRAVITY
                print(f"W = {self.state.theta_dot:>7.4f}rps | H_p = "
                    f"{self.pred_height:6.4f}m | theta = {self.state.theta:>7.4f}r : "
                    f"{self.state.theta*180/np.pi:>6.3f}deg\n")

            else:
                self.int_theta += self.state.theta_dot*dt

            if self.__check_0_crossing_t_d():
                height = (1-np.cos(self.state.theta))*self.length
                error = (height / self.pred_height)
                self.prev_peak = self.state.theta
                #print(f"                      Height = "
                #    f"{height:6.4f}, error = {error:7.4f}")
                if self.swing_count >= 5:
                    self.height_list.append(height)
                    self.j_list.append(error)
                    #print(f"Mean error: {np.mean(self.j_list):7.4f}")

                    torque_error = (GRAVITY*self.length *
                                    np.sin(self.state.theta))/(self.j*self.state.theta_ddot)
                #    print(f"torque error: {torque_error}")


            self.prev_state.theta_dot = self.state.theta_dot
            self.prev_acc_y = self.acc_y
            self.prev_state.time = self.state.time

            self.print_counter = (self.print_counter + 1) % 200
            return 0
        else:
            return 1

    def get_coords(self):

        x_coord = np.sin(self.state.theta)
        y_coord = -np.cos(self.state.theta)
        return x_coord, y_coord

    def get_int_coords(self):

        x_coord = np.sin(self.int_theta)
        y_coord = -np.cos(self.int_theta)
        return x_coord, y_coord

    def get_torque(self):
        # Need to figure this out!!!
        torque = ((self.acc_y - self.g_y) - GRAVITY*np.sin(self.state.theta))/self.sensor_radius
        # if predicted_theta_ddot != 0:
        # self.ddot_error.append(self.theta_ddot/predicted_theta_ddot)
        return torque

    def write_to_csv(self):
        write_string = ""
        for height, j in zip(self.height_list, self.j_list):
            write_string += f"{height},{j}\n"
        write_string = write_string[:-2]
        with open("test-data.csv", "w") as f:
            f.write(write_string)

class State:
    def __init__(self):
        self.time = 0
        self.theta = 0
        self.theta_dot = 0
        self.theta_ddot = 0
        self.acc_y = 0