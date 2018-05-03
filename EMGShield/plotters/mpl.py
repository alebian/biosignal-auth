import logging
import queue
import threading
import time

import matplotlib.pyplot as plt


logger = logging.getLogger()

class DynamicPlotter(object):
    def __init__(self, x_range=5000, min_val=-100, max_val=100,
                 color='r', linewidth=2.0, title='', y_label='', x_label=''):
        plt.ion()

        self.x = [None]*6
        self.x_range = x_range
        self.fig = plt.figure()
        self.ax = [None]*6
        self.line1 = [None]*6
        self.plotx = [None]*6

        for i in range(0,6):
            self.x[i] = []
            self.plotx[i] = []
            self.ax[i] = self.fig.add_subplot(320 + i+1)
            plt.title("channel {0}".format(i))
            plt.xlabel(x_label)
            plt.ylabel(y_label)
            self.line1[i], = self.ax[i].plot(self.x[i], color, linewidth=linewidth, label='X')
            self.ax[i].axis([0, x_range, min_val, max_val])

        self.plcounter = 0
        self.fig.canvas.draw()
        self.counter = 0

    def close(self):
        plt.close()

    def plotdata(self, new_values):
        self.counter+=1
        self.plcounter = self.plcounter + 1
        for i, val in enumerate(new_values):
            self.x[i].append(val)
            self.plotx[i].append(self.plcounter)
            self.line1[i].set_ydata(self.x[i])
            self.line1[i].set_xdata(self.plotx[i])


            if self.plcounter > self.x_range:
                self.plotx[i] = []
                self.x[i] = []

        if self.plcounter > self.x_range:
            self.plcounter = 0

        if self.counter > 25:
            self.counter = 0
            plt.pause(0.00001)

# import matplotlib.pyplot as plt


# class DynamicPlotter:
#     def __init__(self, x_range=5000, min_val=-100, max_val=100,
#                  color='r', title='', y_label='', x_label='', linewidth=2.0):
#         plt.ion()
#         self.x = []

#         self.fig = plt.figure()
#         self.ax = self.fig.add_subplot(111)

#         plt.title(title)
#         plt.xlabel(x_label)
#         plt.ylabel(y_label)
#         self.line1, = self.ax.plot(self.x, color, label='X',linewidth=linewidth)

#         self.x_range = x_range
#         self.ax.axis([0, x_range, min_val, max_val])
#         self.plcounter = 0
#         self.plotx = []
#         self.counter = 0

#     def close(self):
#         plt.close()

#     def plotdata(self, new_values):
#         self.counter+=1
#         self.x.append(new_values)
#         self.plotx.append(self.plcounter)
#         self.line1.set_ydata(self.x)
#         self.line1.set_xdata(self.plotx)
#         # self.fig.canvas.draw()

#         self.plcounter = self.plcounter + 1

#         if self.plcounter > self.x_range:
#             self.plcounter = 0
#             self.plotx[:] = []
#             self.x[:] = []

#         if self.counter > 20:
#             self.counter = 0
#             plt.pause(0.00001)
