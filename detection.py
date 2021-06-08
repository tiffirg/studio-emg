import numpy as np
import matplotlib.pyplot as plt
from scipy.stats.mstats import gmean
from numpy import power, mean, sqrt, asarray
import pandas as pd
import csv
SIZE_EMA = SIZE_RMS = 32
AMOUNT_CHANNELS = 4


class Detection:
    def __init__(self, size_receive_data):
        self.size_receive_data = size_receive_data
        self.is_activity = False
        self.check_activity = False
        self.activity = []
        self.activity_threshold_1 = 2
        self.activity_threshold_2 = 2.5
        self.time_activity = 0
        self.threshold_time_activity = 16
        self.average_value = 0
        self.threshold_amplitude_activity = 60

    def detection_activity(self, average_activity_value, average_value, activity_values, data_for_averaging, data_for_processed):
        if not self.check_activity:
            self.average_value = average_value
        if self.is_activity:
            if average_activity_value / self.average_value > self.activity_threshold_2:
                self.time_activity += 1
                self.activity.extend(activity_values)
            else:
                self.is_activity = False
                self.check_activity = False
                return self.activity, self.time_activity
        else:
            if average_activity_value / self.average_value > self.activity_threshold_1:
                self.check_activity = True
                self.time_activity += 1
                self.activity.extend(activity_values)
                if self.time_activity > self.threshold_time_activity:
                    if any(el > self.threshold_amplitude_activity for el in self.activity):
                        self.is_activity = True
                    else:
                        self.averaging_inactivity(data_for_averaging, data_for_processed)
                        self.check_activity = False
                        self.clear_activity()

            else:
                self.averaging_inactivity(data_for_averaging, data_for_processed)
                self.check_activity = False
                self.clear_activity()

    def averaging_inactivity(self, data_for_averaging, data_for_processed):
        if self.check_activity:
            data_for_processed[:self.size_receive_data] = [self.average_value] * self.size_receive_data
            if self.time_activity > 1:
                number = (self.time_activity - 1) * self.size_receive_data
                data_for_averaging[-number:] = [self.average_value] * number

    def clear_activity(self):
        self.activity = []
        self.time_activity = 0


class Processing:
    def __init__(self):
        self.a_EMA = 2 / (SIZE_EMA + 1)
        self.reverse_a_EMA = 1 - self.a_EMA
        self.previous_results = [0, 0, 0, 0]

    def apply(self, data):
        for i in range(len(data) - SIZE_RMS):
            data[i] = self.calculate_ema(self.calculate_rms(data[i: i + SIZE_RMS]))
        return data

    def apply_init(self, data):
        initital_data = data[:SIZE_RMS]
        initital_value = self.calculate_rms(initital_data)
        data[0] = initital_value
        self.previous_results[1] = initital_value
        for i in range(1, len(data) - SIZE_RMS):
            data[i] = self.calculate_ema(self.calculate_rms(data[i: i + SIZE_RMS]))
        return data

    def calculate_rms(self, data):
        data = np.array(data)
        return sqrt((data ** 2).mean())

    def calculate_ema(self, data):
        result_ema = self.a_EMA * data + self.reverse_a_EMA * self.previous_results[1]
        self.previous_results[1] = result_ema
        return result_ema


file = open("dataset_a71.csv", "a", newline="")
writer = csv.writer(file)
# writer.writerow(["activity0", "activity1", "activity2", "activity3", "label"])
processing = Processing()
detection = Detection(8)
lengths = []

channels = np.genfromtxt(r"C:\Users\legion\PycharmProjects\StudioEmg\data\26.01.2021-17-189-75-Безымянный")[:, :4]
channels -= 305
signal = channels[:, 1]
signal = signal[:signal.shape[0] // 8 * 8]

data_for_averaging = [0] * 128
data_for_processed = [0] * 32
data_emg = [0] * 32

init_data = np.abs(signal[:160])
data_emg[:32] = signal[128: 160]
init_data = processing.apply_init(init_data)
data_for_averaging[:128] = init_data[:128]
data_for_processed[:32] = init_data[128:]
channel = signal.reshape(-1, 8)
result = []
i = 128
plt.figure(0)
for data in channel[20:]:
    data_emg.extend(data)
    data = np.abs(data)
    data_for_processed.extend(data)
    data_for_processed = processing.apply(data_for_processed)
    average_value = gmean(data_for_averaging)
    average_activity_value = max(data_for_processed[:8])
    package_activity = detection.detection_activity(average_activity_value, average_value, data_emg[:8], data_for_averaging, data_for_processed)
    if package_activity is not None:
        activity, length_activity = package_activity
        if length_activity < 75:
            string = [";".join(map(str, channels[i - length_activity * 8: i, j])) for j in range(4)] + ["5"]
            writer.writerow(string)
            lengths.append(length_activity)
            print(i - length_activity * 8, length_activity)
            plt.plot([i - length_activity * 8 for _ in range(601)], list(range(-300, 301)))
            plt.plot([i for _ in range(601)], list(range(-300, 301)))
    data_emg = data_emg[8:]
    data_for_averaging = data_for_averaging[8:]
    data_for_averaging.extend(data_for_processed[:8])
    data_for_processed = data_for_processed[8:]
    i += 8
    result.extend(data_for_averaging[:8])
plt.plot(signal)
plt.figure(1)
plt.plot(result)
print(pd.Series(lengths).describe())
plt.show()
