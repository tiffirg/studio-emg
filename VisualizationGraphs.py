from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QScrollArea, QStyle, QVBoxLayout, QWidget, QGroupBox
from Graphs import WidgetGraphs
from Thread import ReceptionData


class VisualizationGraphs(QWidget):
    def __init__(self, amount_channels):
        super().__init__()
        self.count = 0
        self.path = ''
        self.now_filters = []
        self.amount_channels = amount_channels
        self.group = QGroupBox('', self)
        self.layout_channels = QVBoxLayout(self)
        self.layout = QHBoxLayout(self)
        self.area = QScrollArea(self)
        self.play_btn = QPushButton(self)
        self.save_btn = QPushButton(self)

        self.graphs_widget = WidgetGraphs(amount_channels)
        self.thread = ReceptionData()

        self.initUI()

    def initUI(self):
        self.thread.transfer_data.connect(self.graphs_widget.update_graphs)
        self.layout_channels.setSpacing(0)
        self.layout_channels.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.box_buttons = QGroupBox("", self)
        self.layout_buttons = QHBoxLayout(self)

        self.play_btn.setCheckable(True)
        self.play_btn.setEnabled(False)
        self.play_btn.setMaximumSize(QSize(50, 50))
        self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_btn.clicked.connect(self.play)

        self.save_btn.setCheckable(True)
        self.save_btn.setVisible(False)
        self.save_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.save_btn.clicked.connect(self.save_signal)

        self.layout_buttons.addWidget(self.play_btn)
        self.layout_buttons.addWidget(self.save_btn)
        self.box_buttons.setLayout(self.layout_buttons)
        self.box_buttons.setMaximumSize(QSize(120, 50))
        self.box_buttons.setObjectName("ColoredGroupBox")
        self.box_buttons.setStyleSheet("QGroupBox#ColoredGroupBox { border: 0 px;}")

        self.area.setWidgetResizable(True)
        self.layout_channels.addWidget(self.box_buttons)
        self.layout_channels.addWidget(self.graphs_widget)
        self.group.setLayout(self.layout_channels)
        self.area.setWidget(self.group)
        self.layout.addWidget(self.area)
        self.setLayout(self.layout)

    def update_stream(self, path):
        is_port = False
        self.path = path
        if self.path.startswith("COM"):
            self.save_btn.setVisible(True)
            is_port = True
        else:
            self.save_btn.setVisible(False)
        self.thread.connect(device=path, is_port=is_port)
        self.play_btn.setChecked(True)
        self.play_btn.setEnabled(True)
        self.play()

    def play(self):
        if self.play_btn.isChecked():
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.thread.play()
        else:
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.thread.stop()

    def set_name_save_file(self, name):
        self.thread.set_name_save_file(name)

    def save_signal(self):
        if self.save_btn.isChecked():
            self.save_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
            self.thread.set_save_signal(True)
        else:
            self.save_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
            self.thread.set_save_signal(False)
