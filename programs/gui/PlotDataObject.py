import datetime
import json
import re

from HelperFunctions import HelperFunction as hf, FileExtension


class PlotDataObject:
    def __init__(self, src_path: str):

        # TODO: add plot type, data fields

        self.dir_separator = hf.get_dir_separator()
        self.path = self.format_directory_path(src_path)
        self.metadata_path = self.path + FileExtension.META_FILE.value

        self.data_info = None
        try:
            with open(self.metadata_path, 'r') as f:
                self.data_info = json.load(f)
        except:
            # TODO: exit out here
            pass

        self.slice_info = {
            "begin_date": None,
            "end_date": None,
            "export_data_type": None,
            "lev_min": None,
            "lev_max": None,
            "lon_min": None,
            "lon_max": None,
            "lat_min": None,
            "lat_max": None,
        }

    def set_begin_date(self, date: datetime):
        pass

    def format_directory_path(self, path: str) -> str:
        reg = r"{0}$".format(self.dir_separator)
        if not re.findall(reg, path):
            path += self.dir_separator
        return path

    def get_data_time_range_str(self) -> (str, str, str, str):
        return self.data_info['begin_date'] + " 0:00", self.data_info[
            'end_date'] + " 21:00"

    def get_data_lat_range_str(self) -> (str, str, str):
        return str(hf.round_number(self.data_info['lat_min'], 5)), str(
            hf.round_number(self.data_info['lat_max'],
                            5)), hf.format_variable_name(
                                self.data_info['lat_units'])

    def get_data_lon_range_str(self) -> (str, str, str):
        return str(hf.round_number(self.data_info['lon_min'], 5)), str(
            hf.round_number(self.data_info['lon_max'],
                            5)), hf.format_variable_name(
                                self.data_info['lon_units'])

    def get_data_lev_range_str(self) -> (str, str, str):
        return str(hf.round_number(self.data_info['lev_min'], 5)), str(
            hf.round_number(self.data_info['lev_max'],
                            5)), self.data_info['lev_units']
