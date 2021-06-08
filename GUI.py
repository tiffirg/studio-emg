import sys

import serial.tools.list_ports
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QHBoxLayout, QFileDialog, QInputDialog
from PyQt5.QtWidgets import QMainWindow, QAction, QTabWidget, QWidget
from PyQt5.QtWidgets import QMenu

from VisualizationGraphs import VisualizationGraphs
from datetime import datetime


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Studio'
        self.setWindowTitle(self.title)
        self.central_widget = InterfaceTab()
        self.menu_bar = self.menuBar()
        self.name_port = None
        self.age = "17"
        self.height = "189"
        self.weight = "75"
        self.initUI()

    def initUI(self):
        self.portAction = QMenu('&Порт', self)
        openAction = QAction('&Открыть файл', self)
        openAction.setShortcut('&Ctrl+A')
        openAction.setStatusTip('&Открыть файл')
        openAction.triggered.connect(self.openFile)

        exitAction = QAction('&Закрыть', self)
        exitAction.setShortcut('&Ctrl+Q')
        exitAction.setStatusTip('&Закрыть приложение')
        exitAction.triggered.connect(self.exitCall)
        self.fileMenu = self.menu_bar.addMenu('&Файл')
        self.fileMenu.aboutToShow.connect(self.check_port)
        self.settingsMenu = self.menu_bar.addAction('&Настройки')
        self.settingsMenu.triggered.connect(self.open_settings)
        toolsMenu = self.menu_bar.addMenu('&Tools')
        helpMenu = self.menu_bar.addMenu('&Help')
        self.fileMenu.addMenu(self.portAction)
        self.fileMenu.addAction(openAction)
        self.fileMenu.addAction(exitAction)

        self.setCentralWidget(self.central_widget)

    def check_port(self, port=None):
        ports = self.get_ports()
        if port is not None:
            if port in ports:
                return True
            return False
        if not ports:
            self.portAction.setEnabled(False)
            return
        self.portAction.setEnabled(True)
        for port in ports:
            self.portAction.clear()
            com_port = QAction(port, self)
            com_port.triggered.connect(self.set_port)
            self.portAction.addAction(com_port)
        return

    def set_port(self):
        self.name_port = self.sender().text()
        self.central_widget.update_stream(self.name_port)

    def get_ports(self):
        ports = serial.tools.list_ports.comports()
        return [com.device for com in ports]

    def open_settings(self):
        text, ok = QInputDialog.getText(self, 'Настройки файла', 'Введите название файла:')
        if ok:
            self.set_name_file(text)

    def set_name_file(self, name):
        self.central_widget.set_name_save_file(self.__update_name_file(name))

    def __update_name_file(self, name):
        name = "-".join([datetime.now().strftime("%d.%m.%Y"), self.age, self.height, self.weight, name])
        return name

    def openFile(self):
        path_file, _ = QFileDialog.getOpenFileName(self, "Открыть файл", QDir.homePath())
        if path_file != '':
            self.central_widget.update_stream(path_file)

    def exitCall(self):
        sys.exit(self.exec_())


class InterfaceTab(QWidget):
    def __init__(self):
        super().__init__()
        self.file = ''
        self.tab_widget = QTabWidget(self)
        self.layout = QHBoxLayout(self)
        self.tab_visualization_graphs = VisualizationGraphs(amount_channels=5)
        self.initUI()

    def initUI(self):
        self.tab_widget.addTab(self.tab_visualization_graphs, 'Графики')
        self.tab_widget.setTabShape(0)
        self.tab_widget.setTabPosition(2)
        self.layout.addWidget(self.tab_widget)
        self.setLayout(self.layout)

    def update_stream(self, file):
        self.file = file
        self.tab_visualization_graphs.update_stream(self.file)

    def set_name_save_file(self, name):
        self.tab_visualization_graphs.set_name_save_file(name)
