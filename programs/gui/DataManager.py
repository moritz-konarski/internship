import datetime
import json

import numpy as np
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal

from DataObject import DataObject
from HelperFunctions import FileExtension, PlotType, DataAction, \
    HelperFunction as hf


class DataManager(QThread):
    error = pyqtSignal(str)
    message = pyqtSignal(str)
    preparation_finished = pyqtSignal()

    def __init__(self, path: str):
        super().__init__()
        self.thread_running = False

        self.dir_separator = hf.get_dir_separator()
        self.path = hf.format_directory_path(path)
        self.metadata_path = self.path + FileExtension.META_FILE.value
        self.metadata_dictionary = None
        try:
            with open(self.metadata_path, 'r') as f:
                self.metadata_dictionary = json.load(f)
        except:
            self.error.emit("Cannot Open Metadata File")
            return
        self.var_name = self.metadata_dictionary['name']
        self.data_path = self.path + self.var_name + FileExtension.DATA_FILE.value

        self.selected_data_min = None
        self.selected_data_max = None

        self.begin_date = None
        self.end_date = None
        self.begin_date_index = None
        self.end_date_index = None

        self.lat_min = None
        self.lat_max = None
        self.lat_min_index = None
        self.lat_max_index = None

        self.lon_min = None
        self.lon_max = None
        self.lon_min_index = None
        self.lon_max_index = None

        self.lev_min = None
        self.lev_max = None
        self.lev_min_index = None
        self.lev_max_index = None

        self.data_action = None
        self.plot_type = None

        self.time_counter = None
        self.lev_counter = None
        self.total_files = None

        self.is_iterator_prepared = False

        self.lat_index = None
        self.lon_index = None
        self.lev_index = None
        self.time_index = None

    def prepare_data_iterator(self):
        data = None
        print("lat: " + str(self.lat_min_index))
        print("lat: " + str(self.lat_max_index))
        print("lon: " + str(self.lon_min_index))
        print("lon: " + str(self.lon_max_index))
        print("lev: " + str(self.lev_min_index))
        print("lev: " + str(self.lev_max_index))
        print(self.begin_date)
        print(self.begin_date_index)
        print(self.end_date)
        print(self.end_date_index)
        self.message.emit("Starting data preparation...")
        if self.plot_type == PlotType.HEAT_MAP:
            if len(self.shape) == 4:
                data = np.load(self.data_path, allow_pickle=True)['data'][
                       self.begin_date_index:self.end_date_index + 1,
                       self.lev_max_index:self.lev_min_index + 1,
                       self.lat_min_index:self.lat_max_index + 1,
                       self.lon_min_index:self.lon_max_index + 1]
            else:
                data = np.load(self.data_path, allow_pickle=True)['data'][
                       self.begin_date_index:self.end_date_index + 1,
                       self.lat_min_index: self.lat_max_index + 1,
                       self.lon_min_index:self.lon_max_index + 1]

        elif self.plot_type == PlotType.TIME_SERIES:
            if len(self.shape) == 4:
                data = np.load(self.data_path, allow_pickle=True)['data'][
                       self.begin_date_index:self.end_date_index + 1,
                       self.lev_max_index:self.lev_min_index + 1,
                       self.lat_min_index, self.lon_min_index]
            else:
                data = np.load(self.data_path, allow_pickle=True)['data'][
                       self.begin_date_index:self.end_date_index + 1,
                       self.lat_min_index, self.lon_min_index]

        self.selected_data_min = float(np.nanmin(data))
        self.selected_data_min = float(np.nanmin(data))
        if self.plot_type == PlotType.HEAT_MAP:
            self.time_counter = self.end_date_index - self.begin_date_index + 1
        elif self.plot_type == PlotType.TIME_SERIES:
            self.time_counter = 1
        print(self.time_counter)
        self.lev_counter = self.lev_min_index - self.lev_max_index + 1
        print(self.lev_counter)
        self.total_files = self.time_counter * self.lev_counter
        print(self.total_files)
        self.lev_index = self.lev_max_index
        self.time_index = self.begin_date_index
        self.message.emit("Finished Data Preparation")
        self.is_iterator_prepared = True
        self.preparation_finished.emit()

    @pyqtSlot()
    def run(self):
        if self.is_iterator_prepared:
            pass
        else:
            self.prepare_data_iterator()

    def __next__(self) -> DataObject:
        if self.time_index > self.end_date_index:
            raise StopIteration
        # TODO: create function from time index to time and then pass the times
        data_object = DataObject(self.plot_type, self.var_name,
                                 self.metadata_dictionary['long_name'],
                                 self.metadata_dictionary['units'])
        data_object.set_data_min_max(self.selected_data_min,
                                     self.selected_data_max)
        if self.plot_type == PlotType.HEAT_MAP:
            # TODO: set date
            data_object.set_lon_min_max(self.lon_min, self.lon_max)
            data_object.set_lat_min_max(self.lat_min, self.lat_max)
            if len(self.shape) == 4:
                data = np.load(self.data_path, allow_pickle=True)
                data_object.set_level(float(data['lev'][self.lev_index]))

                # ['data'][
                #       self.begin_date_index:self.end_date_index + 1,
                #       self.lev_max_index:self.lev_min_index + 1,
                #       self.lat_min_index:self.lat_max_index + 1,
                #       self.lon_min_index:self.lon_max_index + 1]
            else:
                data = np.load(self.data_path, allow_pickle=True)
            data_object.set_object_data_min_max(float(np.nanmin(data)),
                                                float(np.nanmax(data)))
            # TODO: turn data into DataFrame
            data_object.set_data(data)

        elif self.plot_type == PlotType.TIME_SERIES:
            data_object.set_start_time(self.begin_date)
            data_object.set_end_time(self.end_date)
            data_object.set_lon_min_max(self.lon_min, 0)
            data_object.set_lat_min_max(self.lat_min, 0)
            if len(self.shape) == 4:
                data = np.load(self.data_path, allow_pickle=True)
                data_object.set_level(float(data['lev'][self.lev_index]))
            else:
                data = np.load(self.data_path, allow_pickle=True)
            data_object.set_object_data_min_max(float(np.nanmin(data)),
                                                float(np.nanmax(data)))
            # TODO: turn data into DataFrame
            data_object.set_data(data)

        if self.lev_index > self.lev_min_index:
            self.lev_index = self.lev_max_index
            self.time_index += 1
        return data_object

    def set_data_action(self, action: DataAction):
        self.data_action = action
        self.is_iterator_prepared = False

    def set_plot_type(self, plot_type: PlotType):
        self.plot_type = plot_type
        self.is_iterator_prepared = False

    def set_begin_time(self, begin_time: str):
        try:
            self.begin_date = hf.get_datetime_from_str(begin_time)
            self.get_begin_time_index()
            if self.begin_date < hf.get_datetime_from_str(
                    self.metadata_dictionary['begin_date'] +
                    " 0:00") or self.begin_date > hf.get_datetime_from_str(
                self.metadata_dictionary['end_date'] + " 21:00"):
                raise Exception()
            if isinstance(self.end_date, datetime.datetime):
                if self.begin_date > self.end_date:
                    raise Exception()
            self.is_iterator_prepared = False
            return True
        except:
            self.error.emit("Incorrect Start Time!")
            self.begin_date = None
            self.begin_date_index = None
        return False

    def get_begin_time_index(self):
        self.begin_date = self.begin_date.replace(
            second=0,
            minute=0,
            microsecond=0,
            hour=int(self.begin_date.hour - self.begin_date.hour %
                     (24 / self.metadata_dictionary['values_per_day'])))
        datetime_delta = self.begin_date - hf.get_datetime_from_str(
            self.metadata_dictionary['begin_date'] + " 0:00")
        self.begin_date_index = int(
            datetime_delta.days * self.metadata_dictionary['values_per_day'] +
            datetime_delta.seconds / 3600 /
            (24 / self.metadata_dictionary['values_per_day']))

    def set_end_time(self, end_time: str):
        try:
            self.end_date = hf.get_datetime_from_str(end_time)
            self.get_end_time_index()
            if self.end_date < hf.get_datetime_from_str(
                    self.metadata_dictionary['begin_date'] +
                    " 0:00") or self.end_date > hf.get_datetime_from_str(
                self.metadata_dictionary['end_date'] + " 21:00"):
                raise Exception()
            if isinstance(self.begin_date, datetime.datetime):
                if self.begin_date > self.end_date:
                    raise Exception()
            self.is_iterator_prepared = False
            return True
        except:
            self.error.emit("Incorrect End Time!")
            self.end_date = None
            self.end_date_index = None
            return False

    def get_end_time_index(self):
        self.end_date = self.end_date.replace(
            second=0,
            minute=0,
            microsecond=0,
            hour=int(self.end_date.hour - self.end_date.hour %
                     (24 / self.metadata_dictionary['values_per_day'])))
        datetime_delta = self.end_date - hf.get_datetime_from_str(
            self.metadata_dictionary['begin_date'] + " 0:00")
        self.end_date_index = int(
            datetime_delta.days * self.metadata_dictionary['values_per_day'] +
            datetime_delta.seconds / 3600 /
            (24 / self.metadata_dictionary['values_per_day']))

    def set_lat_min(self, text: str) -> bool:
        try:
            self.lat_min = float(text)
            self.find_closest_lat_min()
            if not self.lat_max is None:
                if self.lat_max < self.lat_min:
                    raise Exception()
            self.is_iterator_prepared = False
            return True
        except:
            self.error.emit("Incorrect Minimum Latitude!")
            self.lat_min = None
            self.lat_min_index = None
            return False

    def set_lat_max(self, text: str) -> bool:
        try:
            self.lat_max = float(text)
            self.find_closest_lat_max()
            if not self.lat_min is None:
                if self.lat_max < self.lat_min:
                    raise Exception()
            self.is_iterator_prepared = False
            return True
        except:
            self.error.emit("Incorrect Maximum Latitude!")
            self.lat_max = None
            self.lat_max_index = None
            return False

    def find_closest_lat_min(self):
        lats = np.load(self.data_path, allow_pickle=True)['lat'][:]

        best_index = -1
        min_diff = 2 * np.nanmax(lats)
        for (i, opt) in enumerate(lats):
            if abs(opt - self.lat_min) < min_diff:
                best_index = i
                min_diff = abs(opt - self.lat_min)

        self.lat_min = lats[best_index]
        self.lat_min_index = best_index

    def find_closest_lat_max(self):
        lats = np.load(self.data_path, allow_pickle=True)['lat'][:]

        best_index = -1
        min_diff = 2 * np.nanmax(lats)
        for (i, opt) in enumerate(lats):
            if abs(opt - self.lat_max) < min_diff:
                best_index = i
                min_diff = abs(opt - self.lat_max)

        self.lat_max = lats[best_index]
        self.lat_max_index = best_index

    def set_lon_min(self, text: str) -> bool:
        try:
            self.lon_min = float(text)
            self.find_closest_lon_min()
            if not self.lon_max is None:
                if self.lon_max < self.lon_min:
                    raise Exception()
            self.is_iterator_prepared = False
            return True
        except:
            self.error.emit("Incorrect Minimum Longitude!")
            self.lon_min = None
            self.lon_min_index = None
            return False

    def set_lon_max(self, text: str) -> bool:
        try:
            self.lon_max = float(text)
            self.find_closest_lon_max()
            if not self.lon_min is None:
                if self.lon_max < self.lon_min:
                    raise Exception()
            self.is_iterator_prepared = False
            return True
        except:
            self.error.emit("Incorrect Maximum Longitude!")
            self.lon_max = None
            self.lon_max_index = None
            return False

    def find_closest_lon_min(self):
        lons = np.load(self.data_path, allow_pickle=True)['lon'][:]

        best_index = -1
        min_diff = 2 * np.nanmax(lons)
        for (i, opt) in enumerate(lons):
            if abs(opt - self.lon_min) < min_diff:
                best_index = i
                min_diff = abs(opt - self.lon_min)

        self.lon_min = lons[best_index]
        self.lon_min_index = best_index

    def find_closest_lon_max(self):
        lons = np.load(self.data_path, allow_pickle=True)['lon'][:]

        best_index = -1
        min_diff = 2 * np.nanmax(lons)
        for (i, opt) in enumerate(lons):
            if abs(opt - self.lon_max) < min_diff:
                best_index = i
                min_diff = abs(opt - self.lon_max)

        self.lon_max = lons[best_index]
        self.lon_max_index = best_index

    def set_lev_min(self, text: str) -> bool:
        try:
            self.lev_min = float(text)
            self.find_closest_lev_min()
            if not self.lev_max is None:
                if self.lev_max < self.lev_min:
                    raise Exception()
            self.is_iterator_prepared = False
            return True
        except:
            self.error.emit("Incorrect Minimum Level!")
            self.lev_min = None
            self.lev_min_index = None
            return False

    def set_lev_max(self, text: str) -> bool:
        try:
            self.lev_max = float(text)
            self.find_closest_lev_max()
            if not self.lev_min is None:
                if self.lev_max < self.lev_min:
                    raise Exception()
            self.is_iterator_prepared = False
            return True
        except:
            self.error.emit("Incorrect Maximum Level!")
            self.lev_max = None
            self.lev_max_index = None
            return False

    def find_closest_lev_min(self):
        levs = np.load(self.data_path, allow_pickle=True)['lev'][:]

        best_index = -1
        min_diff = 2 * np.nanmax(levs)
        for (i, opt) in enumerate(levs):
            if abs(opt - self.lev_min) < min_diff:
                best_index = i
                min_diff = abs(opt - self.lev_min)

        self.lev_min = levs[best_index]
        self.lev_min_index = best_index

    def find_closest_lev_max(self):
        levs = np.load(self.data_path, allow_pickle=True)['lev'][:]

        best_index = -1
        min_diff = 2 * np.nanmax(levs)
        for (i, opt) in enumerate(levs):
            if abs(opt - self.lev_max) < min_diff:
                best_index = i
                min_diff = abs(opt - self.lev_max)

        self.lev_max = levs[best_index]
        self.lev_max_index = best_index

    @property
    def metadata(self):
        return self.metadata_dictionary

    @property
    def shape(self):
        return self.metadata_dictionary['shape']

    def get_data_time_range_str(self) -> (str, str):
        return self.metadata_dictionary['begin_date'] + " 00:00", \
               self.metadata_dictionary[
                   'end_date'] + " 21:00"

    def get_data_lat_range_str(self) -> (str, str, str):
        return str(hf.round_number(
            self.metadata_dictionary['lat_min'],
            5)), str(hf.round_number(self.metadata_dictionary['lat_max'],
                                     5)), hf.format_variable_name(
            self.metadata_dictionary['lat_units'])

    def get_data_lon_range_str(self) -> (str, str, str):
        return str(hf.round_number(
            self.metadata_dictionary['lon_min'],
            5)), str(hf.round_number(self.metadata_dictionary['lon_max'],
                                     5)), hf.format_variable_name(
            self.metadata_dictionary['lon_units'])

    def get_data_lev_range_str(self) -> (str, str, str):
        return str(hf.round_number(
            self.metadata_dictionary['lev_min'],
            5)), str(hf.round_number(self.metadata_dictionary['lev_max'],
                                     5)), self.metadata_dictionary['lev_units']
