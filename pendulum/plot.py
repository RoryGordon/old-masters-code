import numpy as np

from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

from torque import get_torque, predict_theta
from collectdata import unpack, Data
from sread import Sensor


class Chart:
    def __init__(self, data_objects):
        self.data_objects = data_objects

    def plot_theta(self):
        legend_titles = []
        for data in self.data_objects:
            # plt.plot(data.timestamps, data.theta_dot)
            plt.plot(data.timestamps, data.theta)
            legend_titles.append(data.name)
        plt.legend(legend_titles)
        plt.show()

    def plot_torque(self):
        prediction, torque = get_torque(*self.data_objects)
        '''
        for data in self.data_objects:
            plt.plot(data.timestamps, data.theta_ddot)
        plt.plot(self.data_objects[0].timestamps, prediction)
        '''
        zero_timestamps = self.data_objects[0].get_zero_timestamps()
        zero_torque = []
        for index in self.data_objects[0].theta_zeros:
            zero_torque.append(torque[index])

        plt.plot(self.data_objects[0].timestamps, torque)
        plt.plot(zero_timestamps, zero_torque, "x")
        #plt.legend(("User", "Free", "Prediction", "Torque"))
        plt.ylabel("Torque")
        plt.xlabel("Time /s")
        plt.show()

    def plot_torque_test(self):
        prediction, torque = get_torque(self.data_objects[1],
                                        self.data_objects[1])
        '''
        for data in self.data_objects:
            plt.plot(data.timestamps, data.theta_ddot)
        plt.plot(self.data_objects[0].timestamps, prediction)
        '''
        zero_timestamps = self.data_objects[1].get_zero_timestamps()
        zero_torque = []
        for index in self.data_objects[1].theta_zeros:
            zero_torque.append(torque[index])

        plt.plot(self.data_objects[1].timestamps,
                 self.data_objects[1].filtered_theta_ddot)
        plt.plot(self.data_objects[1].timestamps, prediction)
        plt.plot(zero_timestamps, zero_torque, "x")
        #plt.legend(("User", "Free", "Prediction", "Torque"))
        plt.ylabel("Torque")
        plt.xlabel("Time /s")
        plt.show()

    def plot_theta_vs_theta_ddot(self):
        prediction, torque = get_torque(self.data_objects[1],
                                        self.data_objects[1])
        for data in self.data_objects:
            plt.plot(np.sin(data.theta), data.filtered_theta_ddot)
        plt.plot(np.sin(self.data_objects[1].theta), prediction)
        plt.legend(("User", "Free", "Prediction"))
        plt.show()

    def plot_predicted_theta(self):
        prediction = predict_theta(self.data_objects[1])
        plt.plot(self.data_objects[1].timestamps,
                 self.data_objects[1].theta)
        plt.plot(self.data_objects[1].timestamps,
                 prediction)
        plt.legend(("Free", "Prediction"))
        plt.show()


class J_Plot:
    def __init__(self):
        self.data = [[],[]]
        with open("test-data.csv", "r") as f:
            data_string = f.read()

        for line in data_string.split("\n"):
            line_split = line.split(",")
            for axis, item in zip(self.data, line_split):
                axis.append(float(item))
    
    def plot(self):
        plt.scatter(self.data[0], self.data[1])
        plt.show()


if __name__ == "__main__":
    '''
    user, free = unpack()
    chart = Chart((user, free))
    # chart.plot_theta()
    print(f"User grad: {user.get_gradient()}\n"
          f"Free grad: {free.get_gradient()}")
    chart.plot_torque()
    # chart.plot_torque_test()
    chart.plot_theta_vs_theta_ddot()
    # chart.plot_predicted_theta()
    '''
    J_Plot().plot()
