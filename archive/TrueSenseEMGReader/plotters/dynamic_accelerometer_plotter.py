import matplotlib.pyplot as plt


class DynamicAccelerometerPlotter:
    def __init__(self, x_range=200, min_val=-127, max_val=127, title='Accelerometer'):
        plt.ion()
        self.x = []
        self.y = []
        self.z = []

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)

        plt.title(title)
        self.line1, = self.ax.plot(self.x, 'r', label='X')
        self.line2, = self.ax.plot(self.y, 'g', label='Y')
        self.line3, = self.ax.plot(self.z, 'b', label='Z')

        self.x_range = x_range
        self.ax.axis([0, x_range, min_val, max_val])
        self.plcounter = 0
        self.plotx = []

    def close(self):
        plt.close()

    def plotdata(self, new_values):
        self.x.append(new_values[0])
        self.y.append(new_values[1])
        self.z.append(new_values[2])

        self.plotx.append(self.plcounter)

        self.line1.set_ydata(self.x)
        self.line2.set_ydata(self.y)
        self.line3.set_ydata(self.z)

        self.line1.set_xdata(self.plotx)
        self.line2.set_xdata(self.plotx)
        self.line3.set_xdata(self.plotx)

        self.fig.canvas.draw()
        plt.pause(0.0001)
        self.plcounter = self.plcounter + 1

        if self.plcounter > self.x_range:
            self.plcounter = 0
            self.plotx[:] = []
            self.x[:] = []
            self.y[:] = []
            self.z[:] = []
