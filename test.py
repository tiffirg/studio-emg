import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, pyqtSlot
from serial import Serial


class ReceptionData(QThread):
    transfer_data = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.size = 1000

        self.path = None
        self.stream = None
        self.is_port = None
        self.pause = None
        self.is_save_signal = False
        self.file = None

        self.buffer_string = ""
        self.buffer = []

        self.timer = QTimer()
        self.timer.setTimerType(0)
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.update)

    def start(self, priority=QThread.InheritPriority):
        if self.is_port and self.pause:
            self.reconnect()
        self.timer.start()
        self.pause = False
        super().start()

    def stop(self):
        self.timer.stop()
        self.pause = True

    def set_save_signal(self, value):
        self.is_save_signal = value

    def run(self):
        if self.is_port:
            try:
                self.buffer_string = self.buffer_string + self.stream.read(self.stream.inWaiting()).decode()
                # print("%(buffer_string)r" % {"buffer_string": self.buffer_string})
            except UnicodeDecodeError as error:
                print(error)
            else:
                if '\n' in self.buffer_string:
                    if self.is_save_signal:
                        self.file.writelines(self.buffer_string.rsplit("\n", 1)[0] + "\n")
                    lines = self.buffer_string.lstrip().split("\n")
                    last_received = lines[:-1]
                    self.buffer_string = lines[-1]
                    values = [np.array(el.split(" "), dtype=np.int32) for el in last_received]
                    length_values = len(values)
                    length = len(self.buffer)
                    if length + length_values >= self.size:
                        self.buffer = self.buffer[length + length_values - self.size + 1:]
                    self.buffer = values
                    self.transfer_data.emit(self.buffer)
        else:
            n = 30
            string = ""
            for i in range(n):
                value = self.stream.readline()
                if value == '':
                    # self.connect()
                    # self.repeat_signal.emit()
                    self.run()
                    break
                string += value
            values = [np.array(el.split(" "), dtype=np.int32) for el in string.strip().split("\n")[:-1]]
            length = len(self.buffer)
            if n + length >= self.size:
                self.buffer = self.buffer[length - self.size + n + 1:]
            self.buffer += values
            self.transfer_data.emit(self.buffer)

    def set_path_stream(self, path, it_is_port):
        self.path = path
        self.is_port = it_is_port

    def connect(self):
        if self.path is None:
            return
        if self.stream is not None:
            self.disconnect()
            self.clear_window()
        self.pause = None
        if self.is_port:
            self.stream = Serial(self.path, 115200)
            return
        self.stream = open(self.path, "r")

    def disconnect(self):
        if self.stream is None:
            return
        self.timer.stop()
        self.stream.close()
        self.stream = None
        self.pause = None

    def reconnect(self):
        self.disconnect()
        self.connect()

    def clear_window(self):
        self.buffer = []
        self.filter_buffer = []
        self.buffer_string = ''

    def get_path_stream(self):
        return self.path