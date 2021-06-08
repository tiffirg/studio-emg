import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from serial import Serial
from string import digits
from random import choice
from time import sleep


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
        self.interval = 4
        self.size_receive_data = 8

        self.timer = QTimer()
        self.timer.setTimerType(0)
        # self.timer.setInterval(self.interval)
        self.timer.timeout.connect(self.update)

        self.buffer_string = b""
        self.buffer = []

    def processing_sequence(self, sequence):
        channels = np.empty(5)
        channels[0] = (sequence[0] << 2) | (sequence[1] >> 6)
        channels[1] = ((sequence[1] & 0o77) << 4) | (sequence[2] >> 4)
        channels[2] = ((sequence[2] & 0o17) << 6) | (sequence[3] >> 2)
        channels[3] = ((sequence[3] & 0o3) << 8) | (sequence[4])
        channels[4] = (sequence[5] << 2) | sequence[6]
        if self.is_save_signal:
            self.save_file.write(" ".join(map(str, channels)) + "\n")
        return channels

    def update(self):
        if self.is_port:
            # print(self.stream.inWaiting())
            # data = self.stream.read(self.size_receive_data * 7)
            # new_data = [self.decode_sequence(data[i: i + 7]) for i in range(0, self.size_receive_data * 7, 7)]
            # print(new_data)
            # length = len(self.buffer)
            # if length + self.size_receive_data >= self.size:
            #     self.buffer = self.buffer[length + self.size_receive_data - self.size + 1:]
            # self.buffer += new_data
            # self.transfer_data.emit(self.buffer)

            amount_bytes = self.stream.inWaiting()
            if amount_bytes >= 7:
                amount_pack = amount_bytes // 7
                data = self.stream.read(amount_pack * 7)
                new_data = [self.processing_sequence(data[i: i + 7]) for i in range(0, amount_pack * 7, 7)]
                length = len(self.buffer)
                if length + self.size_receive_data >= self.size:
                    self.buffer = self.buffer[length + self.size_receive_data - self.size + 1:]
                self.buffer += new_data
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
            values = [np.array(el.strip().split(" "), dtype=np.float32) for el in string.strip().split("\n")[:-1]]
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
        self.stream = Serial(self.device, 1000000)
        self.stream.read_until(bytes([1]))
        self.stream.read(self.size_receive_data * 7)

    def connect_file(self):
        self.stream = open(self.device, "r")

    def stop(self):
        self.timer.stop()
        if self.is_port:
            self.disconnect()

    def play(self):
        if self.stream is None and self.is_port:
            self.connect_port()
        self.timer.start(self.interval)

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
