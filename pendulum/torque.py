import numpy as np

#from collectdata import Data, unpack


def get_torque(user, free):
    """Assume free swing, and predict the angular acceleration"""
    gradient = free.get_gradient()

    torque = []
    predicted_theta_ddot = []

    for theta in user.theta:
        predicted_theta_ddot.append(gradient*np.sin(theta))

    for i in range(len(user.filtered_theta_ddot)):
        torque.append(user.filtered_theta_ddot[i] - predicted_theta_ddot[i])

    for i in range(user.theta_zeros[0]):
        torque[i] = 0.
    return predicted_theta_ddot, torque


def predict_theta(data):
    """Assume free swing, return values for theta"""
    gradient = data.get_gradient()
    prediction = []

    for ddot in data.filtered_theta_ddot:
        prediction.append(np.arcsin(ddot/gradient))

    return prediction
