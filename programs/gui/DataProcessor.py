import os
import re
import json
import numpy as np
import platform
from pathlib import Path
from netCDF4 import Dataset
from enum import Enum, auto


class FileExtension(Enum):
    NETCDF = "*.nc"
    NETCDF4 = "*.nc4"
    DATA_FILE = ".npz"
    TMP_DATA_FILE = "_tmp.npz"
    META_FILE = "metadata.json"
    TMP_META_FILE = "metadata_tmp.json"


class DirectorySeparator(Enum):
    UNIX = "/"
    WINDOWS = "\\"


class DataProcessorStatus(Enum):
    IDLE = auto()
    EXTRACTING_DATA = auto()


def format_variable_name(name: str) -> str:
    n = re.sub("_", " ", name)
    return " ".join(w.capitalize() for w in n.split())


class DataProcessor:

    def __init__(self, source_dir: str, destination_dir: str):

        system = platform.system()
        if system == 'Darwin' or system == 'Linux':
            self.__dir_separator = DirectorySeparator.UNIX.value
        elif system == 'Windows':
            self.__dir_separator = DirectorySeparator.WINDOWS.value

        self.__src_dir = self.__format_directory_paths(source_dir)
        self.__dest_dir = self.__format_directory_paths(destination_dir)
        self.__status = DataProcessorStatus.IDLE
        self.__extension = FileExtension.NETCDF4.value
        self.__extraction_progress = 0
        self.__sorted_file_list = sorted(
            Path(self.__src_dir).glob(self.__extension))

    def get_status(self) -> DataProcessorStatus:
        return self.__status

    def get_progress(self) -> float:
        if self.__status == DataProcessorStatus.EXTRACTING_DATA:
            return self.__extraction_progress
        else:
            return -1

    # TODO: append variable name to path
    def __format_directory_paths(self, path: str) -> str:
        reg = r"{0}$".format(self.__dir_separator)
        if not re.findall(reg, path):
            path += self.__dir_separator
        return path

    def extract_variable(self, variable_name: str):

        if variable_name not in self.get_available_variables():
            print("Cannot extract variable")
            exit(-1)

        destination_path = self.__dest_dir + variable_name \
                           + self.__dir_separator

        os.makedirs(destination_path, exist_ok=True)

        self.__status = DataProcessorStatus.EXTRACTING_DATA

        self.__tmp_data_file_path = destination_path + variable_name + \
                                    FileExtension.TMP_DATA_FILE.value

        self.__data_file_path = destination_path + variable_name + \
                                FileExtension.DATA_FILE.value

        self.__extract_and_save_data(variable_name)

        self.__tmp_meta_file_path = destination_path + \
                                    FileExtension.TMP_META_FILE.value

        self.__meta_file_path = destination_path + \
                                FileExtension.META_FILE.value

        self.__extract_metadata(variable_name)

        self.__replace_fill_value()

    def __extract_and_save_data(self, var_name: str):
        data = None
        length = len(self.__sorted_file_list)
        for (i, part) in enumerate(self.__sorted_file_list):
            self.__extraction_progress = (i + 1) / length
            filepath = os.path.join(part)
            with Dataset(filepath, 'r') as d:
                if data is None:
                    data = np.asarray(d.variables[var_name])
                else:
                    data = np.append(data, np.asarray(d.variables[var_name]),
                                     axis=0)
        filepath = os.path.join(self.__sorted_file_list[0])
        with Dataset(filepath, 'r') as d:
            time = np.asarray(d.variables['time'])
            lat = np.asarray(d.variables['lat'])
            lon = np.asarray(d.variables['lon'])
            lev = np.asarray(d.variables['lev'])

        data = data.astype(np.float32, casting='safe')
        time = time.astype(np.int32, casting='safe')
        lat = lat.astype(np.float64, casting='safe')
        lon = lon.astype(np.float64, casting='safe')
        lev = lev.astype(np.float64, casting='safe')

        with open(self.__tmp_data_file_path, 'wb') as f:
            np.savez_compressed(f, data=data, time=time, lat=lat, lon=lon,
                                lev=lev, allow_pickle=True)

    def __replace_fill_value(self, ):
        with open(self.__tmp_meta_file_path, 'r') as f:
            meta_dict = json.load(f)

        if meta_dict['data_max'] == meta_dict['fill_value']:
            d = np.load(self.__tmp_data_file_path, allow_pickle=True)
            if meta_dict['lev_count'] == 0:
                new_d = np.where(d['data'][:, :, :] != meta_dict['fill_value'],
                                 d['data'][:, :, :], np.NaN)
            else:
                new_d = np.where(
                    d['data'][:, :, :, :] != meta_dict['fill_value'],
                    d['data'][:, :, :, :], np.NaN)

            with open(self.__data_file_path, 'wb') as f:
                np.savez_compressed(f, data=new_d, time=d['time'], lat=d['lat'],
                                    lon=d['lon'], lev=d['lev'],
                                    allow_pickle=True)
            os.remove(self.__tmp_data_file_path)

            if len(new_d.shape) == 4:
                data_max = float(np.nanmax(new_d[:, :, :, :]))
                data_min = float(np.nanmin(new_d[:, :, :, :]))
            else:
                data_max = float(np.nanmax(new_d[:, :, :]))
                data_min = float(np.nanmin(new_d[:, :, :]))
            meta_dict['data_max'] = data_max
            meta_dict['data_min'] = data_min

            with open(self.__meta_file_path, 'w') as f:
                json.dump(meta_dict, f)
            os.remove(self.__tmp_meta_file_path)

        else:
            os.rename(self.__data_data_file_path, self.__data_file_path)
            os.rename(self.__tmp_meta_file_path, self.__meta_file_path)

    def __extract_metadata(self, variable_name: str):
        with Dataset(self.__sorted_file_list[0], 'r') as d:
            name = str(d.variables[variable_name].name)
            long_name = format_variable_name(
                d.variables[variable_name].long_name)
            std_name = format_variable_name(
                d.variables[variable_name].standard_name)
            units = str(d.variables[variable_name].units)
            fill_value = float(d.variables[variable_name]._FillValue)
            lat_units = str(d.variables['lat'].units)
            lon_units = str(d.variables['lon'].units)
            lev_units = str(d.variables['lev'].units)
            begin_date = str(d.RangeBeginningDate)
        with Dataset(self.__sorted_file_list[-1], 'r') as d:
            end_date = str(d.RangeEndingDate)

        d = np.load(self.__tmp_data_file_path, allow_pickle=True)
        shape = d['data'].shape
        time_steps = int(d['time'].shape[0])
        lat_min = float(d['lat'].min())
        lat_max = float(d['lat'].max())
        lon_min = float(d['lon'].min())
        lon_max = float(d['lon'].max())
        lev_min = float(d['lev'].min())
        lev_max = float(d['lev'].max())
        if len(shape) == 4:
            data_max = float(d['data'][:, :, :, :].max())
            data_min = float(d['data'][:, :, :, :].min())
        else:
            data_max = float(d['data'][:, :, :].max())
            data_min = float(d['data'][:, :, :].min())

        info_dict = {
            "name": name,
            "long_name": long_name,
            "std_name": std_name,
            "units": units,
            "shape": shape,
            "data_max": data_max,
            "data_min": data_min,
            "values_per_day": time_steps,
            "day_count": int(shape[0] / time_steps),
            "begin_date": begin_date,
            "end_date": end_date,
            "last_day_inclusive": True,
            "lat_min": lat_min,
            "lat_max": lat_max,
            "lat_count": int(shape[-2]),
            "lat_units": lat_units,
            "lon_min": lon_min,
            "lon_max": lon_max,
            "lon_count": int(shape[-1]),
            "lon_units": lon_units,
            "lev_min": lev_min,
            "lev_max": lev_max,
            "lev_count": 0 if len(shape) != 4 else int(shape[1]),
            "lev_units": lev_units,
            "fill_value": fill_value
        }
        with open(self.__tmp_meta_file_path, 'w') as f:
            json.dump(info_dict, f)

    def get_variable_information(self) -> [(str, str, str)]:
        var_info_list = []
        with Dataset(self.__sorted_file_list[0], 'r') as d:
            for var in d.variables.keys():
                var_info_list.append(
                    (var, d.variables[var].long_name, d.variables[var].units))
        return var_info_list

    def get_available_variables(self) -> [str]:
        var_info_list = []
        with Dataset(self.__sorted_file_list[0], 'r') as d:
            for var in d.variables.keys():
                if var != 'time' and var != 'lat' and var != 'lon' and var != 'lev':
                    var_info_list.append(var)
        return var_info_list

    def extract_all(self):
        var_name_list = self.get_available_variables()
        print(var_name_list)
        for var_name in var_name_list:
            self.extract_variable(var_name)
