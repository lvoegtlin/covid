import numpy as np


def logistic(t, a, b, c, d):
    return c + (d - c) / (1 + a * np.exp(- b * t))


def exponential(t, a, b, c):
    return a * np.exp(b * t) + c