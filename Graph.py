import pyqtgraph as pg
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


class GraphWidget(pg.GraphicsWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.sizeWindowX = 1000
        self.sizeWindowY = 700
        self.plot_signal = self.addPlot()
        self.curve_signal = self.plot_signal.plot(pen='b')
        self.initUI()

    def initUI(self):
        self.plot_signal.setYRange(-self.sizeWindowY // 2, self.sizeWindowY // 2, padding=0)
        self.plot_signal.setXRange(0, self.sizeWindowX, padding=0)
        self.plot_signal.showGrid(x=True, y=True, alpha=0.8)
        self.plot_signal.disableAutoRange(axis="xy")

    def update(self, data):
        self.curve_signal.setData(data)