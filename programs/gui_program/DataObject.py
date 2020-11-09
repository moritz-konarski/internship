from datetime import datetime

import pandas as pd

from HelperFunctions import PlotType


class DataObject:
    def __init__(self, plot_type: PlotType, name: str, long_name: str,
                 unit: str):
        self.plot_type = plot_type
        self.data = None

        self.name = name
        self.long_name = long_name
        self.unit = unit

        self.lats = None
        self.lons = None

        self.start_time = None
        self.end_time = None

        self.data_min = None
        self.data_max = None

        self.object_data_min = None
        self.object_data_max = None

        self.level = None

        self.lat_min = None
        self.lat_max = None

        self.lon_min = None
        self.lon_max = None

    def set_lons(self, lons):
        self.lons = lons

    def set_lats(self, lats):
        self.lats = lats

    def set_data(self, data: pd.DataFrame):
        self.data = data

    def get_data(self) -> pd.DataFrame:
        return self.data

    def get_name(self) -> str:
        return self.name

    def get_unit(self) -> str:
        return self.unit

    def get_long_name(self) -> str:
        return self.long_name

    def set_start_time(self, time: datetime):
        self.start_time = time

    def get_start_time(self) -> datetime:
        return self.start_time

    def set_end_time(self, time: datetime):
        self.end_time = time

    def get_end_time(self) -> datetime:
        return self.end_time

    def set_data_min_max(self, min: float, max: float):
        self.data_min = min
        self.data_max = max

    def get_data_min_max(self) -> (float, float):
        return self.data_min, self.data_max

    def set_object_data_min_max(self, min: float, max: float):
        self.object_data_min = min
        self.object_data_max = max

    def get_object_data_min_max(self) -> (float, float):
        return self.object_data_min, self.object_data_max

    def set_level(self, level: float):
        self.level = level

    def get_level(self) -> float:
        return self.level

    def set_lon_min_max(self, min: float, max: float):
        self.lon_min = min
        self.lon_max = max

    def get_lon_min_max(self) -> (float, float):
        return self.lon_min, self.lon_max

    def set_lat_min_max(self, min: float, max: float):
        self.lat_min = min
        self.lat_max = max

    def get_lat_min_max(self) -> (float, float):
        return self.lat_min, self.lat_max
