import datetime
import json
import re

from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal

from HelperFunctions import FileExtension, HelperFunction as hf
from PlotObject import PlotType


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

    def set_begin_time(self, begin_time: str):
        try:
            self.begin_date = hf.get_datetime_from_str(begin_time)
            if self.begin_date < hf.get_datetime_from_str(self.metadata_dictionary['begin_date'] + " 0:00"):
                raise Exception()
            if isinstance(self.end_date, datetime.datetime):
                if self.begin_date > self.end_date:
                    raise Exception()
        except:
            self.error.emit("Incorrect Start Time!")
            pass

    def set_end_time(self, end_time: str):
        try:
            self.end_date = hf.get_datetime_from_str(end_time)
            if self.end_date > hf.get_datetime_from_str(self.metadata_dictionary['end_date'] + " 21:00"):
                raise Exception()
            if isinstance(self.begin_date, datetime.datetime):
                if self.begin_date < self.end_date:
                    raise Exception()
        except:
            self.error.emit("Incorrect End Time!")
            pass

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

    def get_data_time_range_str(self) -> (str, str, str, str):
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
