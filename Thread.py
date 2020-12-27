import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from serial import Serial
from string import digits
from random import choice


class ReceptionData(QThread):
    transfer_data = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.device = None
        self.is_port = None
        self.stream = None

        self.save_file = None
        self.name_save_file = self.generate_name_save_file()
        self.is_save_signal = False
        self.size = 1000
        self.interval = 1

        self.timer = QTimer()
        self.timer.setTimerType(0)
        self.timer.setInterval(self.interval)
        self.timer.timeout.connect(self.update)

        self.buffer_string = ""
        self.buffer = []

    def update(self):
        if self.is_port:
            try:
                self.buffer_string = self.buffer_string + self.stream.read(self.stream.inWaiting()).decode()
                # print("%(buffer_string)r" % {"buffer_string": self.buffer_string})
            except UnicodeDecodeError as error:
                print(error)
            else:
                if '\n' in self.buffer_string:
                    if self.is_save_signal:
                        self.save_file.writelines(self.buffer_string.rsplit("\n", 1)[0] + "\n")
                    lines = self.buffer_string.lstrip().split("\n")
                    last_received = lines[:-1]
                    self.buffer_string = lines[-1]
                    values = [np.array(el.split(" "), dtype=np.int32) for el in last_received]
                    length_values = len(values)
                    length = len(self.buffer)
                    if length + length_values >= self.size:
                        self.buffer = self.buffer[length + length_values - self.size + 1:]
                    self.buffer += values
                    self.transfer_data.emit(self.buffer)
        else:
            n = 8
            string = ""
            for i in range(n):
                value = self.stream.readline()
                if value == '':
                    self.connect(self.device, self.is_port)
                    break
                string += value
            values = [np.array(el.split(" "), dtype=np.int32) for el in string.strip().split("\n")[:-1]]
            length = len(self.buffer)
            if n + length >= self.size:
                self.buffer = self.buffer[length - self.size + n + 1:]
            self.buffer += values
            self.transfer_data.emit(self.buffer)

    def connect(self, device, is_port):
        self.disconnect()
        self.device = device
        self.is_port = is_port
        if self.is_port:
            self.connect_port()
            return
        self.connect_file()
        self.start()

    def disconnect(self):
        if self.stream is None:
            return
        self.close()
        self.stream.close()
        self.stream = None

    def connect_port(self):
        self.stream = Serial(self.device, 2000000)

    def connect_file(self):
        self.stream = open(self.device, "r")

    def stop(self):
        self.timer.stop()
        if self.is_port:
            self.disconnect()

    def play(self):
        if self.stream is None and self.is_port:
            self.connect_port()
        self.timer.start()

    def close(self):
        self.quit()
        self.wait()

    def set_name_save_file(self, name):
        self.name_save_file = name

    def set_save_signal(self, value):
        self.is_save_signal = value
        if value:
            self.save_file = open("data\\" + self.name_save_file, "w")
        else:
            self.save_file = None
            self.name_save_file = self.generate_name_save_file()

    def generate_name_save_file(self):
        return ''.join(choice(digits) for _ in range(10))
