from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal

from DataManager import DataManager
from DataObject import DataObject
from HelperFunctions import ExportDataType, PlotType, HelperFunction as hf


class ExportData(QThread):
    is_exporting = pyqtSignal(bool)
    finished = pyqtSignal()

    def __init__(self, data_manager: DataManager):
        super().__init__()
        self.data_object = None
        self.path = None
        self.file_name = None
        self.export_file_type = None
        self.data_manager = data_manager
        self.is_running = False

    def set_attributes(self, data_type: str,
                       path: str):
        self.export_file_type = data_type
        self.path = path

    def update_attributes(self, data_object: DataObject):
        if not self.is_running:
            return
        if data_object.plot_type == PlotType.TIME_SERIES:
            if len(self.data_manager.shape) == 4:
                self.file_name = "Time Series " + data_object.long_name + " " + hf.get_str_from_datetime(
                    data_object.start_time) + "-" + hf.get_str_from_datetime(
                    data_object.end_time) + " (" + str(
                    data_object.lat_min) + "N, " + str(
                    data_object.lon_min) + "E) " + str(
                    data_object.level) + " hPa"
            else:
                self.file_name = "Time Series " + data_object.long_name + " " + hf.get_str_from_datetime(
                    data_object.start_time) + "-" + hf.get_str_from_datetime(
                    data_object.end_time) + " (" + str(
                    data_object.lat_min) + "N, " + str(
                    data_object.lon_min) + "E)"

    def export_files(self):
        self.is_exporting.emit(True)
        for data_object in iter(self.data_manager):
            if not self.is_running:
                self.is_exporting.emit(False)
                return
            self.update_attributes(data_object)
            if self.export_file_type == ExportDataType.CSV.value:
                data_object.data.to_csv(
                    self.path + self.file_name + ExportDataType.CSV.value)
            elif self.export_file_type == ExportDataType.EXCEL.value:
                data_object.data.to_excel(
                    self.path + self.file_name + ExportDataType.EXCEL.value)
            elif self.export_file_type == ExportDataType.HTML.value:
                data_object.data.to_html(
                    self.path + self.file_name + ExportDataType.HTML.value)
            elif self.export_file_type == ExportDataType.ZIP.value:
                data_object.data.to_pickle(
                    self.path + self.file_name + ExportDataType.ZIP.value)
        self.is_exporting.emit(False)
        self.finished.emit()

    @pyqtSlot()
    def run(self):
        self.is_running = True
        self.export_files()

    def stop(self):
        self.is_running = False
