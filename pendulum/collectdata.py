import os
import scipy

import numpy as np

from scipy.signal import find_peaks
from scipy.signal import savgol_filter
from scipy.integrate import cumtrapz


class Data():
    def __init__(self, userinput, name=None):
        self.name = name
        (self.timestamps,
            self.a_r,
            self.a_theta,
            self.theta_dot) = (userinput[:, 0],
                               userinput[:, 1],
                               userinput[:, 2],
                               userinput[:, 3])
        self.length = len(self.timestamps)

        self.theta_ddot, self.filtered_theta_ddot = self.__diff_theta_dot()
        self.theta_zeros = self.__find_zero_points()
        self.theta = self.__get_theta()

    def __diff_theta_dot(self):
        """Calculate values for angular acceleration"""
        theta_ddot = np.gradient(self.theta_dot,
                                 self.timestamps)

        filtered_theta_ddot = savgol_filter(theta_ddot,
                                            window_length=25,
                                            polyorder=3)

        return theta_ddot, filtered_theta_ddot

    def __find_zero_points(self):
        """Return list of points where theta == 0"""
        filtered_a_r = savgol_filter(self.a_r,
                                     window_length=21,
                                     polyorder=2)
        theta_zeros, _ = find_peaks(filtered_a_r, prominence=0.5)
        return theta_zeros

    def get_zero_timestamps(self):
        zero_timestamps = []
        for zero in self.theta_zeros:
            zero_timestamps.append(self.timestamps[zero])
        return zero_timestamps

    def __get_theta(self):
        start = self.theta_zeros[0]
        theta_int_once = cumtrapz(self.theta_dot[start:],
                                  self.timestamps[start:],
                                  initial=0)
        theta_fix = np.zeros(self.length)
        # put the hard integrated theta between the first 2 zeros
        theta_fix[start:] = theta_int_once

        prev_zero = start
        for zero in self.theta_zeros[1:]:
            # isolate section to integrate, including next zero
            time_section = self.timestamps[prev_zero: zero+1]
            theta_dot_section = self.theta_dot[prev_zero: zero+1]

            # make the integration
            theta_section = cumtrapz(theta_dot_section,
                                     time_section,
                                     initial=0)

            # find the drift at the end of the section
            drift = theta_section[-1]

            # generate a vector increasing steadily from 0
            # to the drift over that time frame
            drift_vec = np.linspace(start=0,
                                    stop=drift,
                                    num=zero-prev_zero+1)

            # make the correction so the last theta=0
            theta_fix[prev_zero: zero] = theta_section[:-1]-drift_vec[:-1]

            # store the zero point for the next loop
            prev_zero = zero
        return theta_fix

    def get_gradient(self):
        """Calculate \frac{lMg}{J}"""
        start = self.theta_zeros[0]

        x = np.sin(self.theta)[start:]
        y = self.filtered_theta_ddot[start:]
        print(f"x length: {len(x)}, y length: {len(y)}")
        # fit a line through all of the data points
        p = np.polyfit(x, y, deg=1)[0]

        return p

    def force_func(self, corrections):
        (theta_factor,
         gradient_factor,
         theta_offset) = corrections

        theta = self.theta*theta_factor + theta_offset
        theta_ddot = self.filtered_theta_ddot * theta_factor
        p = self.get_gradient() * gradient_factor
        force = theta_ddot[self.theta_zeros[0]:] - p*np.sin(theta[self.theta_zeros[0]:])
        return sum(abs(force))


def unpack():
    """Extract data from csv and return Data objects"""
    # Get path name for this script
    script_directory = os.path.dirname(os.path.realpath(__file__))
    # Split by seperators, to make it easier to append
    split_dir = script_directory.split(os.path.sep)
    # Remove the last element to be in the parent directory
    split_dir.pop()


    # Gather and unpack data from CSV
    userinput_file = os.path.sep.join(split_dir + ["data",
                                                   "adafruitmay26th",
                                                   "onesidepush2.csv"])
    userinput = np.genfromtxt(userinput_file, delimiter=',')

    freeswing_file = os.path.sep.join(split_dir + ["data",
                                                   "adafruitmay26th",
                                                   "freeswing.csv"])
    freeswing = np.genfromtxt(freeswing_file, delimiter=',')

    user_data = Data(userinput, "user")
    freeswing_data = Data(freeswing, "freeswing")

    return user_data, freeswing_data


if __name__ == "__main__":
    user, free = unpack()
    print(user.theta_zeros)
    print(user.a_theta)
    print(user.theta)
