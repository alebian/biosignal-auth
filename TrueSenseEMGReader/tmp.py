import json
import numpy as np
import matplotlib.pyplot as plt
import pywt


def save_real_plot(name, data):
    fig, ax = plt.subplots( nrows=1, ncols=1 )
    ax.plot(range(0, len(data)), data, color='green')

    # add a title
    plt.title("Test")

    # add a label to the y-axis
    plt.ylabel("?")
    fig.savefig(name)
    plt.close(fig) 
def save_im_plot(name, data):
    fig, ax = plt.subplots( nrows=1, ncols=1 )
    ax.scatter(data.real,data.imag)

    # add a title
    plt.title("Test")

    # add a label to the y-axis
    plt.ylabel("?")
    fig.savefig(name)
    plt.close(fig) 
def get_data(filepath):
    with open(filepath) as data:
        d = json.load(data)
        return d['adc_values']


def get_hand_diff():
    for i in range(1, 6):
        values = get_data("C:/Users/Luis/src/biosignal-auth/TrueSenseEMGReader/collected_data/alejandro/close_hand_{0}_2017-10-13.json".format(i))
        dvalues = np.diff(values,n=1, axis=-1)
        save_real_plot("{0}diff".format(i), dvalues)


def get_hand_images():
    for i in range(1,6):
        values = get_data("C:/Users/Luis/src/biosignal-auth/TrueSenseEMGReader/collected_data/alejandro/close_hand_{0}_2017-10-13.json".format(i))
        save_real_plot("{0}".format(i), values)
def get_hand_fft():
    for i in range(1,6):
        values = get_data("C:/Users/Luis/src/biosignal-auth/TrueSenseEMGReader/collected_data/alejandro/close_hand_{0}_2017-10-13.json".format(i))
        fftvalues = np.fft.fft(values)
        print(fftvalues)
        save_im_plot("{0}fft".format(i), fftvalues)


# filter_size = 9
# for i in range(1,6):
#     filtered = []
#     values = get_data("C:/Users/Luis/src/biosignal-auth/TrueSenseEMGReader/collected_data/alejandro/close_hand_{0}_2017-10-13.json".format(i))
#     for k in range(0, len(values)):
#         if (k > 2 and k < len(values) - 3):
#             filtered.append(sum(values[k-4:k+5])/9)
#         else:
#             filtered.append(values[k])
#     save_real_plot("{0}filtered".format(i), filtered)

for i in range(1,6):
    values = get_data("C:/Users/Luis/src/biosignal-auth/TrueSenseEMGReader/collected_data/alejandro/close_hand_{0}_2017-10-13.json".format(i))
    wav = pywt.Wavelet('db2')
    cA5 = pywt.wavedec(values, wav, level=5)
    #cd[:] = 0.0

    save_real_plot("{0}wavelet".format(i), cA5[0])