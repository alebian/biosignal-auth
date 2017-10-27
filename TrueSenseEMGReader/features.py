import math


def integrated_emg(data):
    """
    IEMG is calculated as the summation of the absolute values of the sEMG signal amplitude.
    Generally, IEMG is used as an onset index to detect the muscle activity that used
    to oncoming the control command of assistive control device.
    """
    return math.fsum(abs(x) for x in data)


def mean_absolute_value(data):
    """
    MAV is similar to average rectified value (ARV). It can be calculated using the moving average
    of full-wave rectified EMG.
    It is an easy way for detection of muscle contraction levels and it is a popular feature
    used in myoelectric control application
    """
    return integrated_emg(data) / len(data)


def modified_mean_absolute_value_1(data):
    """
    MMAV1 is an extension of MAV using weighting window function wn.
    """
    N = len(data)
    wn = lambda x: 1 if (x >= 0.25 * N and x <= 0.75 * N) else 0.5
    return math.fsum(abs(x) * wn(x) for x in data) / N


def _mmav2_wn(x, N):
    if x >= 0.25 * N and x <= 0.75 * N:
        return 1
    elif x < 0.25 * N:
        return 4 * x / N
    elif x > 0.75 * N:
        return 4 * (x - N) / N


def modified_mean_absolute_value_2(data):
    """
    MMAV2 is similar to MMAV1. However, the smooth window is improved in this method using
    continuous weighting window function wn.
    """
    N = len(data)
    return math.fsum(abs(x) * _mmav2_wn(x, N) for x in data) / N


def mean_absolute_value_slope(data):
    """
    MAVSLP is a modified version of MAV. The differences between the MAVs of adjacent
    segments are determined.
    """


def simple_square_integral(data):
    """
    (SSI) uses the energy of the sEMG signal as a feature.
    """
    return math.fsum(math.pow(abs(x), 2) for x in data)


def variance_of_emg(data):
    """
    VAR uses the power of the sEMG signal as a feature. Generally, the variance is the mean value
    of the square of the deviation of that variable. However, mean of EMG signal is close to zero.
    """
    return math.fsum(math.pow(x, 2) for x in data) / (len(data) - 1)


def root_mean_square(data):
    """
    (RMS) is modeled as amplitude modulated Gaussian random process whose RMS is related to
    the constant force and non-fatiguing contraction. It relates to standard deviation.
    """
    return math.sqrt(math.fsum(math.pow(x, 2) for x in data) / len(data))


if __name__ == '__main__':
    a = [1, 2, 3, 4, -5]
    print(integrated_emg(a))
    print(mean_absolute_value(a))
    print(modified_mean_absolute_value_1(a))
    print(modified_mean_absolute_value_2(a))
    print(simple_square_integral(a))
    print(variance_of_emg(a))
    print(root_mean_square(a))
