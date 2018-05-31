import math


THRESHOLD = 0.1


def integrated_emg(data):
    """
    (IEMG) is calculated as the summation of the absolute values of the sEMG signal amplitude.
    Generally, IEMG is used as an onset index to detect the muscle activity that used
    to oncoming the control command of assistive control device.
    """
    return math.fsum(abs(x) for x in data)


def mean_absolute_value(data):
    """
    (MAV) is similar to average rectified value (ARV). It can be calculated using the moving average
    of full-wave rectified EMG.
    It is an easy way for detection of muscle contraction levels and it is a popular feature
    used in myoelectric control application
    """
    return integrated_emg(data) / len(data)


def modified_mean_absolute_value_1(data):
    """
    (MMAV1) is an extension of MAV using weighting window function wn.
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
    (MMAV2) is similar to MMAV1. However, the smooth window is improved in this method using
    continuous weighting window function wn.
    """
    N = len(data)
    return math.fsum(abs(x) * _mmav2_wn(x, N) for x in data) / N


def mean_absolute_value_slope(data, i = 1):
    """
    (MAVSLP) is a modified version of MAV. The differences between the MAVs of adjacent
    segments are determined.
    """
    if i <= 0:
        raise IndexError('i should be larger than 0')
    if i >= len(data) - 1:
        raise IndexError('i should be less than {}'.format(len(data) - 1))

    return mean_absolute_value(data[0:(i + 1)]) - mean_absolute_value(data[0:i])


def simple_square_integral(data):
    """
    (SSI) uses the energy of the sEMG signal as a feature.
    """
    return math.fsum(math.pow(abs(x), 2) for x in data)


def variance_of_emg(data):
    """
    (VAR) uses the power of the sEMG signal as a feature. Generally, the variance is the mean value
    of the square of the deviation of that variable. However, mean of EMG signal is close to zero.
    """
    return math.fsum(math.pow(x, 2) for x in data) / (len(data) - 1)


def root_mean_square(data):
    """
    (RMS) is modeled as amplitude modulated Gaussian random process whose RMS is related to
    the constant force and non-fatiguing contraction. It relates to standard deviation.
    """
    return math.sqrt(math.fsum(math.pow(x, 2) for x in data) / len(data))


def waveform_length(data):
    """
    (WL) is the cumulative length of the waveform over the time segment. WL is related to the
    waveform amplitude, frequency and time.
    """
    ans = 0.0
    for i in range(0, len(data) - 1):
        ans += abs(data[i + 1] - data[i])
    return ans


def zero_crossing(data, threshold = THRESHOLD):
    """
    (ZC) is the number of times that the amplitude value of sEMG signal crosses the zero y-axis. In
    EMG feature, the threshold condition is used to abstain from the background noise.
    This feature provides an approximate estimation of frequency domain properties.
    """
    count = 0
    for i in range(0, len(data) - 1):
        if data[i] * data[i + 1] < 0:
            if math.fabs(data[i] - data[i + 1]) >= threshold:
                count += 1
    return count


def _slope_sign_change_f(x, threshold = THRESHOLD):
    return 1 if x >= threshold else 0


def slope_sign_change(data, threshold = THRESHOLD):
    """
    (SSC) is similar to ZC. It is another method to represent the frequency information of sEMG
    signal. The number of changes between positive and negative slope among three consecutive
    segments are performed with the threshold function for avoiding the interference in sEMG signal.
    """
    ans = 0.0
    for i in range(1, len(data) - 1):
        ans += _slope_sign_change_f((data[i] - data[i - 1]) * (data[i] - data[i + 1]), threshold)
    return ans


def willison_amplitude(data, threshold = THRESHOLD):
    """
    (WAMP) is the number of times that the difference between sEMG signal amplitude among
    two adjacent segments that exceeds a predefined threshold to reduce noise effects same as
    ZC and SSC.
    """
    ans = 0.0
    for i in range(0, len(data) - 1):
        ans += _slope_sign_change_f(math.fabs(data[i] - data[i + 1]), threshold)
    return ans


FEATURES = {
    "integrated_emg": integrated_emg,
    "mean_absolute_value": mean_absolute_value,
    #"modified_mean_absolute_value_1": modified_mean_absolute_value_1,
    #"modified_mean_absolute_value_2": modified_mean_absolute_value_2,
    #"mean_absolute_value_slope": mean_absolute_value_slope,
    "simple_square_integral": simple_square_integral,
    "variance_of_emg": variance_of_emg,
    "root_mean_square": root_mean_square,
    "waveform_length": waveform_length,
    #"zero_crossing": zero_crossing,
    #"slope_sign_change": slope_sign_change,
    #"willison_amplitude": willison_amplitude
}