import datetime
import json
import platform
import re

import numpy as np
import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from HelperFunctions import DirectorySeparator, FileExtension, HelperFunction
from PlotDataObject import PlotDataObject
from PlotObject import PlotType


class DataManager(QThread):
    def __init__(self, path: str, plot_data_object: PlotDataObject):
        super().__init__()
        self.thread_running = False
        self.plot_data_object = plot_data_object

        self.dir_separator = HelperFunction.get_dir_separator()
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
        self.begin_datetime = datetime.datetime.strptime(
            self.metadata_dictionary['begin_date'] + " " + "0", "%Y-%m-%d %H")
        self.end_datetime = datetime.datetime.strptime(
            self.metadata_dictionary['end_date'] + " " + "21", "%Y-%m-%d %H")

        self.level_count = self.metadata_dictionary['lev_count']
        self.lat_min = self.metadata_dictionary['lat_min']
        self.lat_max = self.metadata_dictionary['lat_max']
        self.lon_min = self.metadata_dictionary['lon_min']
        self.lon_max = self.metadata_dictionary['lon_max']

    def get_data(self, start_time: datetime, end_time: datetime):
        self.get_data(start_time, end_time, 0)

    def get_data(self, start_time: datetime, end_time: datetime, level: int):
        self.check_time_constraints(start_time, end_time)

        if self.level_count == 0:
            pass
        else:
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
