import datetime
import json
import re

import numpy as np

from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal

from HelperFunctions import FileExtension, HelperFunction as hf
from PlotObject import PlotType

# TODO: check lev input

class DataManager(QThread):
    error = pyqtSignal(str)

    def __init__(self, path: str):
        super().__init__()
        self.thread_running = False

        self.dir_separator = hf.get_dir_separator()
        self.path = self.format_directory_path(path)
        self.metadata_path = self.path + FileExtension.META_FILE.value
        self.metadata_dictionary = None
        try:
            with open(self.metadata_path, 'r') as f:
                self.metadata_dictionary = json.load(f)
        except:
            # TODO: exit out here
            pass
        self.var_name = self.metadata_dictionary['name']
        self.data_path = self.path + self.var_name + FileExtension.DATA_FILE.value

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

    def set_begin_time(self, begin_time: str):
        try:
            self.begin_date = hf.get_datetime_from_str(begin_time)
            self.get_begin_time_index()
            if self.begin_date < hf.get_datetime_from_str(self.metadata_dictionary['begin_date'] + " 0:00") or self.begin_date > hf.get_datetime_from_str(self.metadata_dictionary['end_date'] + " 21:00"):
                raise Exception()
            if isinstance(self.end_date, datetime.datetime):
                if self.begin_date > self.end_date:
                    raise Exception()
            return True
        except:
            self.error.emit("Incorrect Start Time!")
            self.begin_date = None
            self.begin_date_index = None
            return False

    def get_begin_time_index(self):
        self.begin_date = self.begin_date.replace(second=0, minute=0, microsecond=0, hour=int(self.begin_date.hour - self.begin_date.hour % (24 / self.metadata_dictionary['values_per_day'])))
        datetime_delta = hf.get_datetime_from_str(self.metadata_dictionary['begin_date'] + " 0:00") - self.begin_date
        self.begin_date_index = int(datetime_delta.days * self.metadata_dictionary['values_per_day'] +
                    datetime_delta.seconds / 3600 /
                    (24 / self.metadata_dictionary['values_per_day']))

    def set_end_time(self, end_time: str):
        try:
            self.end_date = hf.get_datetime_from_str(end_time)
            self.get_end_time_index()
            if self.end_date < hf.get_datetime_from_str(self.metadata_dictionary['begin_date'] + " 0:00") or self.end_date > hf.get_datetime_from_str(self.metadata_dictionary['end_date'] + " 21:00"):
                raise Exception()
            if isinstance(self.begin_date, datetime.datetime):
                if self.begin_date > self.end_date:
                    raise Exception()
            return True
        except:
            self.error.emit("Incorrect End Time!")
            self.end_date = None
            self.end_date_index = None
            return False

    def get_end_time_index(self):
        self.end_date = self.end_date.replace(second=0, minute=0, microsecond=0, hour=int(self.end_date.hour - self.end_date.hour % (24 / self.metadata_dictionary['values_per_day'])))
        datetime_delta = hf.get_datetime_from_str(self.metadata_dictionary['end_date'] + " 0:00")- self.end_date
        self.end_date_index = int(datetime_delta.days * self.metadata_dictionary['values_per_day'] +
                    datetime_delta.seconds / 3600 /
                    (24 / self.metadata_dictionary['values_per_day']))

    def set_lat_min(self, text: str) -> bool:
        try:
            self.lat_min = float(text)
            self.find_closest_lat_min()
            if not self.lat_max is None:
                if self.lat_max < self.lat_min:
                    raise Exception()
            return True
        except:
            self.error.emit("Incorrect Minimum Latetude!")
            self.lat_min = None
            self.lat_min_index = 0
            return False

    def set_lat_max(self, text: str) -> bool:
        try:
            self.lat_max = float(text)
            self.find_closest_lat_max()
            if not self.lat_min is None:
                if self.lat_max < self.lat_min:
                    raise Exception()
            return True
        except:
            self.error.emit("Incorrect Maximum Latetude!")
            self.lat_max = None
            self.lat_max_index = None
            return False

    def find_closest_lat_min(self):
        lats = np.load(self.data_path, allow_pickle=True)['lat'][:]

        best_index = -1
        min_diff = np.nanmax(lats)
        for (i, opt) in enumerate(lats):
            if abs(opt - self.lat_min) < min_diff:
                best_index = i
                min_diff = abs(opt - self.lat_min)

        self.lat_min = lats[best_index]
        self.lat_min_index = best_index

    def find_closest_lat_max(self):
        lats = np.load(self.data_path, allow_pickle=True)['lat'][:]

        best_index = -1
        min_diff = np.nanmax(lats)
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
            return True
        except:
            self.error.emit("Incorrect Minimum Longitude!")
            self.lon_min = None
            self.lon_min_index = 0
            return False

    def set_lon_max(self, text: str) -> bool:
        try:
            self.lon_max = float(text)
            self.find_closest_lon_max()
            if not self.lon_min is None:
                if self.lon_max < self.lon_min:
                    raise Exception()
            return True
        except:
            self.error.emit("Incorrect Maximum Longitude!")
            self.lon_max = None
            self.lon_max_index = None
            return False

    def find_closest_lon_min(self):
        lons = np.load(self.data_path, allow_pickle=True)['lon'][:]

        best_index = -1
        min_diff = np.nanmax(lons)
        for (i, opt) in enumerate(lons):
            if abs(opt - self.lon_min) < min_diff:
                best_index = i
                min_diff = abs(opt - self.lon_min)

        self.lon_min = lons[best_index]
        self.lon_min_index = best_index

    def find_closest_lon_max(self):
        lons = np.load(self.data_path, allow_pickle=True)['lon'][:]

        best_index = -1
        min_diff = np.nanmax(lons)
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
            return True
        except:
            self.error.emit("Incorrect Minimum Level!")
            self.lev_min = None
            self.lev_min_index = 0
            return False

    def set_lev_max(self, text: str) -> bool:
        try:
            self.lev_max = float(text)
            self.find_closest_lev_max()
            if not self.lev_min is None:
                if self.lev_max < self.lev_min:
                    raise Exception()
            return True
        except:
            self.error.emit("Incorrect Maximum Level!")
            self.lev_max = None
            self.lev_max_index = None
            return False

    def find_closest_lev_min(self):
        levs = np.load(self.data_path, allow_pickle=True)['lev'][:]

        best_index = -1
        min_diff = np.nanmax(levs)
        for (i, opt) in enumerate(levs):
            if abs(opt - self.lev_min) < min_diff:
                best_index = i
                min_diff = abs(opt - self.lev_min)

        self.lev_min = levs[best_index]
        self.lev_min_index = best_index

    def find_closest_lev_max(self):
        levs = np.load(self.data_path, allow_pickle=True)['lev'][:]

        best_index = -1
        min_diff = np.nanmax(levs)
        for (i, opt) in enumerate(levs):
            if abs(opt - self.lev_max) < min_diff:
                best_index = i
                min_diff = abs(opt - self.lev_max)

        self.lev_max = levs[best_index]
        self.lev_max_index = best_index

    def check_time_constraints(self, start_time: datetime,
                               end_time: datetime) -> bool:
        if start_time < self.begin_datetime:
            # TODO: error out
            pass
        if end_time < self.end_datetime:
            # TODO: error out
            pass

    def check_location_constraints(self, lat: float, lon: float) -> bool:
        if lat < self.lat_min or lat > self.lat_max:
            # TODO: error out
            pass
        if lon < self.lon_min or lon > self.lon_max:
            # TODO: error out
            pass

    def check_level_constraints(self, level: int) -> bool:
        if level < 0 or level > self.level_count:
            # TODO: error out
            pass

    def get_time_series_data(self, start_time: datetime, end_time: datetime,
                             level: int, lat: float, lon: float):
        self.check_time_constraints(start_time, end_time)
        self.check_location_constraints(lat, lon)
        self.check_level_constraints(level)

        pass

    def get_heat_map_data(self, start_time: datetime, end_time: datetime,
                          level: int):
        self.check_time_constraints(start_time, end_time)
        self.check_level_constraints(level)

        pass

    def format_directory_path(self, path: str) -> str:
        reg = r"{0}$".format(self.dir_separator)
        if not re.findall(reg, path):
            path += self.dir_separator
        return path

    @pyqtSlot()
    def run(self):
        self.thread_running = True

    def stop(self):
        self.thread_running = False

    @property
    def metadata(self):
        return self.metadata_dictionary

    @property
    def shape(self) -> int:
        return self.metadata_dictionary['shape']

    def get_plot_data(self, plot_type: PlotType):
        # return the appropriate type of slice
        pass

    def get_data_time_range_str(self) -> (str, str):
        return self.metadata_dictionary['begin_date'] + " 0:00", self.metadata_dictionary[
            'end_date'] + " 21:00"

    def get_data_lat_range_str(self) -> (str, str, str):
        return str(hf.round_number(self.metadata_dictionary['lat_min'], 5)), str(
            hf.round_number(self.metadata_dictionary['lat_max'],
                            5)), hf.format_variable_name(
                                self.metadata_dictionary['lat_units'])

    def get_data_lon_range_str(self) -> (str, str, str):
        return str(hf.round_number(self.metadata_dictionary['lon_min'], 5)), str(
            hf.round_number(self.metadata_dictionary['lon_max'],
                            5)), hf.format_variable_name(
                                self.metadata_dictionary['lon_units'])

    def get_data_lev_range_str(self) -> (str, str, str):
        return str(hf.round_number(self.metadata_dictionary['lev_min'], 5)), str(
            hf.round_number(self.metadata_dictionary['lev_max'],
                            5)), self.metadata_dictionary['lev_units']
