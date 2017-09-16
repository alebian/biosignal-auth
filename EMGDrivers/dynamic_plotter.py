import matplotlib.pyplot as plt


class DynamicPlotter:
    def __init__(self, range=5000, min_val=-100, max_val=100):
        plt.ion()
        self.x = []

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)

        self.line1, = self.ax.plot(self.x, 'r', label='X')

        self.range = range
        self.ax.axis([0, range, min_val, max_val])
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

        if self.plcounter > self.range:
            self.plcounter = 0
            self.plotx[:] = []
            self.x[:] = []
