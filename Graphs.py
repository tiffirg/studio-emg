import numpy as np
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from Graph import GraphWidget


class WidgetGraphs(QWidget):
    def __init__(self, amount_channels):
        super().__init__()
        self.layout = QVBoxLayout()
        self.graphs = [GraphWidget(parent=self) for _ in range(amount_channels)]
        self.initUI()

    def initUI(self):
        for graph in self.graphs:
            self.layout.addWidget(graph)

        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)

    @pyqtSlot(list)
    def update_graphs(self, data):
        data = np.array(data) - 305
        for i, graph in enumerate(self.graphs):
            graph.update(data[:, i])
