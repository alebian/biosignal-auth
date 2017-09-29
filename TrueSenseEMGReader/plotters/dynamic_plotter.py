import matplotlib.pyplot as plt


class DynamicPlotter:
    def __init__(self, x_range=5000, min_val=-100, max_val=100,
                 color='r', title='', y_label='', x_label=''):
        plt.ion()
        self.x = []

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)

        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        self.line1, = self.ax.plot(self.x, color, label='X')

        self.x_range = x_range
        self.ax.axis([0, x_range, min_val, max_val])
        self.plcounter = 0
        self.plotx = []

    def close(self):
        plt.close()

    def plotdata(self, new_values):
        self.x.append(new_values)
        self.plotx.append(self.plcounter)
        self.line1.set_ydata(self.x)
        self.line1.set_xdata(self.plotx)
        self.fig.canvas.draw()
        plt.pause(0.0001)
        self.plcounter = self.plcounter + 1

        if self.plcounter > self.x_range:
            self.plcounter = 0
            self.plotx[:] = []
            self.x[:] = []
