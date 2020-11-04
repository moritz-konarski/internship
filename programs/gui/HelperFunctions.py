import os
import re
import json
import platform
import numpy as np
from enum import Enum
from pathlib import Path
from netCDF4 import Dataset


class ExportDataType(Enum):
    CSV = ".csv"
    ZIP = ".zip"    # via pickle
    EXCEL = ".xlsx"
    HTML = ".html"


class FileExtension(Enum):
    NETCDF = "*.nc"
    NETCDF4 = "*.nc4"
    DATA_FILE = ".npz"
    TMP_DATA_FILE = "_tmp.npz"
    META_FILE = "metadata.json"
    TMP_META_FILE = "metadata_tmp.json"
    PLOT_PNG = ".png"
    PLOT_PDF = ".pdf"


class DirectorySeparator(Enum):
    UNIX = "/"
    WINDOWS = "\\"


class HelperFunction:
    @staticmethod
    def can_read_directory(src_path: str) -> bool:
        return os.access(src_path, os.R_OK)

    @staticmethod
    def can_write_directory(src_path: str) -> bool:
        return os.access(src_path, os.W_OK)

    @staticmethod
    def get_qt_text_width(element, text: str) -> int:
        return 1.1 * element.fontMetrics().boundingRect(text).width()

    @staticmethod
    def replace_array_fill_value(data: np.ndarray, fill_value) -> np.ndarray:
        if len(data.shape) == 3:
            new_d = np.where(data[:, :, :] != fill_value, data[:, :, :],
                             np.NaN)
        else:
            new_d = np.where(data[:, :, :, :] != fill_value, data[:, :, :, :],
                             np.NaN)
        return new_d

    @staticmethod
    def get_long_variable_name(src_path: str, variable_name: str) -> str:
        sorted_file_list = sorted(
            Path(src_path).glob(FileExtension.NETCDF4.value))
        if len(sorted_file_list) == 0:
            return ""
        with Dataset(sorted_file_list[0], 'r') as d:
            return HelperFunction.format_variable_name(
                d.variables[variable_name].long_name)

    @staticmethod
    def get_available_variables(src_path: str) -> [str]:
        sorted_file_list = sorted(
            Path(src_path).glob(FileExtension.NETCDF4.value))
        var_info_list = []
        if HelperFunction.is_valid_nc_source_directory(src_path):
            with Dataset(sorted_file_list[0], 'r') as d:
                for var in d.variables.keys():
                    if var != 'time' and var != 'lat' and var != 'lon' and var != 'lev':
                        var_info_list.append(var)
        return var_info_list

    @staticmethod
    def is_valid_nc_source_directory(src_path: str) -> bool:
        sorted_file_list = sorted(
            Path(src_path).glob(FileExtension.NETCDF4.value))
        if len(sorted_file_list) == 0:
            return False
        return True

    @staticmethod
    def is_valid_npz_source_directory(src_path: str) -> bool:
        dir_separator = HelperFunction.get_dir_separator()
        reg = r"{0}$".format(dir_separator)
        if not re.findall(reg, src_path):
            src_path += dir_separator

        metadata_path = src_path + FileExtension.META_FILE.value

        metadata_dictionary = None
        try:
            with open(metadata_path, 'r') as f:
                metadata_dictionary = json.load(f)
        except:
            # TODO: exit out here
            pass

        var_name = metadata_dictionary['name']
        data_path = src_path + var_name + FileExtension.DATA_FILE.value
        try:
            np.load(data_path)
            return True
        except:
            return False

    @staticmethod
    def get_dir_separator() -> str:
        system = platform.system()
        if system == 'Darwin' or system == 'Linux':
            return DirectorySeparator.UNIX.value
        elif system == 'Windows':
            return DirectorySeparator.WINDOWS.value

    @staticmethod
    def format_variable_name(name: str) -> str:
        n = re.sub("_", " ", name)
        return " ".join(w.capitalize() for w in n.split())

    @staticmethod
    def get_data_info(src_folder: str):
        with open(src_folder + FileExtension.META_FILE.value, 'r') as f:
            return json.load(f)
