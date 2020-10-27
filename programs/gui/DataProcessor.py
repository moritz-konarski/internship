import os
import re
import json
import numpy as np
import platform
from pathlib import Path
from netCDF4 import Dataset
from enum import Enum
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal


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
    ALLOCATING_MEMORY = "Allocating Memory..."
    EXTRACTING_DATA = "Extracting Data..."
    CONVERTING_DATA_TYPES = "Converting Data Types..."
    REPLACING_FILL_VALUES = "Replacing Fill Values..."
    SAVING_DATA = "Saving Data..."
    EXTRACTING_METADATA = "Extracting Metadata..."
    FINISHED = "Finished!"


class DataProcessor(QThread):
    extraction_progress_update = pyqtSignal(float)
    extraction_status_message = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, source_dir: str, destination_dir: str, var_name: str):
        super().__init__()

        # determine system platform
        system = platform.system()
        if system == 'Darwin' or system == 'Linux':
            self.__dir_separator = DirectorySeparator.UNIX.value
        elif system == 'Windows':
            self.__dir_separator = DirectorySeparator.WINDOWS.value

        self.__src_dir = self.__format_directory_paths(source_dir)
        self.__dest_dir = self.__format_directory_paths(destination_dir)

        self.__status = None
        self.__extension = FileExtension.NETCDF4.value
        self.__extraction_progress = 0
        self.__sorted_file_list = sorted(
            Path(self.__src_dir).glob(self.__extension))
        self.variable_name = var_name
        if len(self.__sorted_file_list) == 0:
            print("No valid files in directory")
            exit(-1)

    @staticmethod
    def __format_variable_name(name: str) -> str:
        n = re.sub("_", " ", name)
        return " ".join(w.capitalize() for w in n.split())

    def __format_directory_paths(self, path: str) -> str:
        reg = r"{0}$".format(self.__dir_separator)
        if not re.findall(reg, path):
            path += self.__dir_separator
        return path

    @pyqtSlot()
    def run(self):
        self.__extract_variable()
        self.finished.emit()

    # extracting the specified variable
    def __extract_variable(self):
        destination_path = self.__dest_dir + self.variable_name \
                           + self.__dir_separator

        os.makedirs(destination_path, exist_ok=True)

        self.__tmp_data_file_path = destination_path + self.variable_name + \
                                    FileExtension.TMP_DATA_FILE.value

        self.__data_file_path = destination_path + self.variable_name + \
                                FileExtension.DATA_FILE.value

        self.__tmp_meta_file_path = destination_path + \
                                    FileExtension.TMP_META_FILE.value

        self.__meta_file_path = destination_path + \
                                FileExtension.META_FILE.value

        self.__extract_and_save_data()

        self.extraction_progress_update.emit(100)

        self.__status = DataProcessorStatus.FINISHED
        self.extraction_status_message.emit(self.__status.value)

    def __extract_and_save_data(self):

        self.__status = DataProcessorStatus.ALLOCATING_MEMORY
        self.extraction_status_message.emit(self.__status.value)

        filepath = os.path.join(self.__sorted_file_list[0])
        with Dataset(filepath, 'r') as d:
            time = np.asarray(d.variables['time'])
            lat = np.asarray(d.variables['lat'])
            lon = np.asarray(d.variables['lon'])
            lev = np.asarray(d.variables['lev'])
            var_dims = len(d.variables[self.variable_name].shape)
            fill_value = d.variables[self.variable_name]._FillValue

        file_count = len(self.__sorted_file_list)
        time_count = time.shape[0]
        lat_count = lat.shape[0]
        lon_count = lon.shape[0]
        lev_count = lev.shape[0]

        self.__status = DataProcessorStatus.EXTRACTING_DATA
        self.extraction_status_message.emit(self.__status.value)

        data = None

        if var_dims == 3:
            data = np.ones((file_count * time_count, lat_count, lon_count),
                           dtype=np.float32)
            for (i, part) in enumerate(self.__sorted_file_list):
                self.__extraction_progress = (i + 1) / file_count
                self.extraction_progress_update.emit(
                    self.__extraction_progress * 100 - 1)

                filepath = os.path.join(part)
                with Dataset(filepath, 'r') as d:
                    _d = np.asarray(d.variables[self.variable_name])
                    data[i * time_count:i * time_count + time_count, :, :] = _d
        elif var_dims == 4:
            data = np.ones(
                (file_count * time_count, lev_count, lat_count, lon_count),
                dtype=np.float32)

            for (i, part) in enumerate(self.__sorted_file_list):
                self.__extraction_progress = (i + 1) / file_count
                self.extraction_progress_update.emit(
                    self.__extraction_progress * 100 - 1)

                filepath = os.path.join(part)
                with Dataset(filepath, 'r') as d:
                    _d = np.asarray(d.variables[self.variable_name])
                    data[i * time_count:i * time_count +
                         time_count, :, :, :] = _d
        else:
            print("unsupported data dimensions")
            exit(-1)

        self.__status = DataProcessorStatus.CONVERTING_DATA_TYPES
        self.extraction_status_message.emit(self.__status.value)

        data = data.astype(np.float32, casting='safe')
        time = time.astype(np.int32, casting='safe')
        lat = lat.astype(np.float64, casting='safe')
        lon = lon.astype(np.float64, casting='safe')
        lev = lev.astype(np.float64, casting='safe')

        self.__status = DataProcessorStatus.REPLACING_FILL_VALUES
        self.extraction_status_message.emit(self.__status.value)

        new_data = self.__replace_fill_value(data, fill_value)

        data_min = float(np.nanmin(new_data))
        data_max = float(np.nanmax(new_data))

        self.__status = DataProcessorStatus.SAVING_DATA
        self.extraction_status_message.emit(self.__status.value)

        with open(self.__data_file_path, 'wb') as f:
            np.savez_compressed(f,
                                data=new_data,
                                time=time,
                                lat=lat,
                                lon=lon,
                                lev=lev,
                                allow_pickle=True)

        self.__status = DataProcessorStatus.EXTRACTING_METADATA
        self.extraction_status_message.emit(self.__status.value)

        self.__extract_metadata(data_min, data_max)

    @staticmethod
    def __replace_fill_value(data: np.ndarray, fill_value) -> np.ndarray:
        if len(data.shape) == 3:
            new_d = np.where(data[:, :, :] != fill_value, data[:, :, :],
                             np.NaN)
        else:
            new_d = np.where(data[:, :, :, :] != fill_value, data[:, :, :, :],
                             np.NaN)
        return new_d

    def __extract_metadata(self, data_min, data_max):
        with Dataset(self.__sorted_file_list[0], 'r') as d:
            name = str(d.variables[self.variable_name].name)
            long_name = DataProcessor.__format_variable_name(
                d.variables[self.variable_name].long_name)
            std_name = DataProcessor.__format_variable_name(
                d.variables[self.variable_name].standard_name)
            units = str(d.variables[self.variable_name].units)
            fill_value = float(d.variables[self.variable_name]._FillValue)
            lat_units = str(d.variables['lat'].units)
            lon_units = str(d.variables['lon'].units)
            lev_units = str(d.variables['lev'].units)
            begin_date = str(d.RangeBeginningDate)
        with Dataset(self.__sorted_file_list[-1], 'r') as d:
            end_date = str(d.RangeEndingDate)

        d = np.load(self.__data_file_path, allow_pickle=True)
        shape = d['data'].shape
        time_steps = int(d['time'].shape[0])
        lat_min = float(d['lat'].min())
        lat_max = float(d['lat'].max())
        lon_min = float(d['lon'].min())
        lon_max = float(d['lon'].max())
        lev_min = float(d['lev'].min())
        lev_max = float(d['lev'].max())

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

        with open(self.__meta_file_path, 'w') as f:
            json.dump(info_dict, f)

    def __get_variable_information(self) -> (str, str, str):
        with Dataset(self.__sorted_file_list[0], 'r') as d:
            return (self.variable_name,
                    d.variables[self.variable_name].long_name,
                    d.variables[self.variable_name].units)

    @staticmethod
    def get_available_variables(src_path: str) -> [str]:
        sorted_file_list = sorted(
            Path(src_path).glob(FileExtension.NETCDF4.value))
        var_info_list = []
        with Dataset(sorted_file_list[0], 'r') as d:
            for var in d.variables.keys():
                if var != 'time' and var != 'lat' and var != 'lon' and var != 'lev':
                    var_info_list.append(var)
        return var_info_list
