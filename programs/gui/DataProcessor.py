import json
import os
import platform
import re
from enum import Enum
from pathlib import Path

import numpy as np
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal
from netCDF4 import Dataset

from HelperFunctions import FileExtension, HelperFunction

# TODO: dont save lev for 3D data


class DataProcessorStatus(Enum):
    ALLOCATING_MEMORY = "Allocating Memory..."
    EXTRACTING_DATA = "Extracting Data..."
    CONVERTING_DATA_TYPES = "Converting Data Types..."
    REPLACING_FILL_VALUES = "Replacing Fill Values..."
    SAVING_DATA = "Saving Data..."
    EXTRACTING_METADATA = "Extracting Metadata..."
    FINISHED = "Finished!"
    THREAD_KILLED = "Thread was killed!"


class DataProcessor(QThread):
    extraction_progress_update = pyqtSignal(float)
    extraction_status_message = pyqtSignal(str)
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, source_dir: str, destination_dir: str, var_name: str):
        super().__init__()

        self.thread_running = False
        # determine system platform
        system = platform.system()
        self.dir_separator = HelperFunction.get_dir_separator()

        self.src_dir = self.format_directory_path(source_dir)
        self.dest_dir = self.format_directory_path(destination_dir)

        self.status = None
        self.file_extension = FileExtension.NETCDF4.value
        self.extraction_progress = 0
        self.sorted_file_list = sorted(
            Path(self.src_dir).glob(self.file_extension))
        self.variable_name = var_name

        self.tmp_data_file_path = ""
        self.data_file_path = ""
        self.tmp_meta_file_path = ""
        self.meta_file_path = ""

        if len(self.sorted_file_list) == 0:
            self.error.emit("Data Processor: Invalid Directory")
            return

    def format_directory_path(self, path: str) -> str:
        reg = r"{0}$".format(self.dir_separator)
        if not re.findall(reg, path):
            path += self.dir_separator
        return path

    @pyqtSlot()
    def run(self):
        self.thread_running = True
        self.extract_variable()
        self.finished.emit()

    @pyqtSlot()
    def stop(self):
        self.thread_running = False
        self.wait()

    # extracting the specified variable
    def extract_variable(self):
        if not self.thread_running:
            self.status = DataProcessorStatus.THREAD_KILLED
            self.extraction_status_message.emit(self.status.value)
            return
        destination_path = self.dest_dir + self.variable_name \
                           + self.dir_separator

        os.makedirs(destination_path, exist_ok=True)

        self.tmp_data_file_path = destination_path + self.variable_name + \
                                  FileExtension.TMP_DATA_FILE.value

        self.data_file_path = destination_path + self.variable_name + \
                              FileExtension.DATA_FILE.value

        self.tmp_meta_file_path = destination_path + \
                                  FileExtension.TMP_META_FILE.value

        self.meta_file_path = destination_path + \
                              FileExtension.META_FILE.value

        if not self.thread_running:
            self.status = DataProcessorStatus.THREAD_KILLED
            self.extraction_status_message.emit(self.status.value)
            return
        self.extract_and_save_data()

        if not self.thread_running:
            self.status = DataProcessorStatus.THREAD_KILLED
            self.extraction_status_message.emit(self.status.value)
            return
        self.extraction_progress_update.emit(100)

        if not self.thread_running:
            self.status = DataProcessorStatus.THREAD_KILLED
            self.extraction_status_message.emit(self.status.value)
            return
        self.status = DataProcessorStatus.FINISHED
        self.extraction_status_message.emit(self.status.value)

    def extract_and_save_data(self):

        self.extraction_progress_update.emit(0)
        self.status = DataProcessorStatus.ALLOCATING_MEMORY
        self.extraction_status_message.emit(self.status.value)

        if not self.thread_running:
            self.status = DataProcessorStatus.THREAD_KILLED
            self.extraction_status_message.emit(self.status.value)
            return
        filepath = os.path.join(self.sorted_file_list[0])
        with Dataset(filepath, 'r') as d:
            time = np.asarray(d.variables['time'])
            lat = np.asarray(d.variables['lat'])
            lon = np.asarray(d.variables['lon'])
            lev = np.asarray(d.variables['lev'])
            var_dims = len(d.variables[self.variable_name].shape)
            fill_value = d.variables[self.variable_name]._FillValue

        file_count = len(self.sorted_file_list)
        time_count = time.shape[0]
        lat_count = lat.shape[0]
        lon_count = lon.shape[0]
        lev_count = lev.shape[0]

        self.status = DataProcessorStatus.EXTRACTING_DATA
        self.extraction_status_message.emit(self.status.value)
        if not self.thread_running:
            self.status = DataProcessorStatus.THREAD_KILLED
            self.extraction_status_message.emit(self.status.value)
            return

        if var_dims == 3:
            data = np.ones((file_count * time_count, lat_count, lon_count),
                           dtype=np.float32)
            for (i, part) in enumerate(self.sorted_file_list):
                if not self.thread_running:
                    self.status = DataProcessorStatus.THREAD_KILLED
                    self.extraction_status_message.emit(self.status.value)
                    return
                self.extraction_progress = (i + 1) / file_count
                self.extraction_progress_update.emit(self.extraction_progress *
                                                     100 - 1)

                filepath = os.path.join(part)
                with Dataset(filepath, 'r') as d:
                    _d = np.asarray(d.variables[self.variable_name])
                    data[i * time_count:i * time_count + time_count, :, :] = _d
        elif var_dims == 4:
            data = np.ones(
                (file_count * time_count, lev_count, lat_count, lon_count),
                dtype=np.float32)

            for (i, part) in enumerate(self.sorted_file_list):
                if not self.thread_running:
                    self.status = DataProcessorStatus.THREAD_KILLED
                    self.extraction_status_message.emit(self.status.value)
                    return
                self.extraction_progress = (i + 1) / file_count
                self.extraction_progress_update.emit(self.extraction_progress *
                                                     100 - 1)

                filepath = os.path.join(part)
                with Dataset(filepath, 'r') as d:
                    _d = np.asarray(d.variables[self.variable_name])
                    data[i * time_count:i * time_count +
                         time_count, :, :, :] = _d
        else:
            self.error.emit("Data Processor: Data Dimension not supported!")
            return

        self.status = DataProcessorStatus.CONVERTING_DATA_TYPES
        self.extraction_status_message.emit(self.status.value)

        data = data.astype(np.float32, casting='safe')
        time = time.astype(np.int32, casting='safe')
        lat = lat.astype(np.float64, casting='safe')
        lon = lon.astype(np.float64, casting='safe')
        lev = lev.astype(np.float64, casting='safe')

        self.status = DataProcessorStatus.REPLACING_FILL_VALUES
        self.extraction_status_message.emit(self.status.value)
        if not self.thread_running:
            self.status = DataProcessorStatus.THREAD_KILLED
            self.extraction_status_message.emit(self.status.value)
            return

        new_data = HelperFunction.replace_array_fill_value(data, fill_value)

        data_min = float(np.nanmin(new_data))
        data_max = float(np.nanmax(new_data))

        self.status = DataProcessorStatus.SAVING_DATA
        self.extraction_status_message.emit(self.status.value)
        if not self.thread_running:
            self.status = DataProcessorStatus.THREAD_KILLED
            self.extraction_status_message.emit(self.status.value)
            return

        with open(self.data_file_path, 'wb') as f:
            np.savez_compressed(f,
                                data=new_data,
                                time=time,
                                lat=lat,
                                lon=lon,
                                lev=lev,
                                allow_pickle=True)

        self.status = DataProcessorStatus.EXTRACTING_METADATA
        self.extraction_status_message.emit(self.status.value)
        if not self.thread_running:
            self.status = DataProcessorStatus.THREAD_KILLED
            self.extraction_status_message.emit(self.status.value)
            return

        self.extract_metadata(data_min, data_max)

    def extract_metadata(self, data_min, data_max):
        with Dataset(self.sorted_file_list[0], 'r') as d:
            name = str(d.variables[self.variable_name].name)
            long_name = HelperFunction.format_variable_name(
                d.variables[self.variable_name].long_name)
            std_name = HelperFunction.format_variable_name(
                d.variables[self.variable_name].standard_name)
            units = str(d.variables[self.variable_name].units)
            fill_value = float(d.variables[self.variable_name]._FillValue)
            lat_units = str(d.variables['lat'].units)
            lon_units = str(d.variables['lon'].units)
            lev_units = str(d.variables['lev'].units)
            begin_date = str(d.RangeBeginningDate)
        with Dataset(self.sorted_file_list[-1], 'r') as d:
            end_date = str(d.RangeEndingDate)
        if not self.thread_running:
            self.status = DataProcessorStatus.THREAD_KILLED
            self.extraction_status_message.emit(self.status.value)
            return

        d = np.load(self.data_file_path, allow_pickle=True)
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
        if not self.thread_running:
            self.status = DataProcessorStatus.THREAD_KILLED
            self.extraction_status_message.emit(self.status.value)
            return

        with open(self.meta_file_path, 'w') as f:
            json.dump(info_dict, f)
