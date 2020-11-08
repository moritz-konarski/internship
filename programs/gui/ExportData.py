from PyQt5.QtCore import QThread

from DataObject import DataObject
from HelperFunctions import ExportDataType, PlotType, HelperFunction as hf


class ExportData(QThread):
    def __init__(self):
        super().__init__()
        self.data_object = None
        self.path = None
        self.file_name = None
        self.export_file_type = None

    def set_attributes(self, data_object: DataObject, data_type: str,
                       path: str):
        self.export_file_type = data_type
        self.data_object = data_object
        self.path = path

        if self.data_object.plot_type == PlotType.TIME_SERIES:
            self.file_name = "Time Series " + self.data_object.long_name + " " + hf.get_str_from_datetime(
                self.data_object.start_time) + "-" + hf.get_str_from_datetime(
                self.data_object.end_time) + " (" + str(
                self.data_object.lat_min) + "N, " + str(
                self.data_object.lon_min) + "E) " + str(
                self.data_object.level) + " hPa"

    def export_file(self):
        if self.data_type == ExportDataType.CSV.value:
            self.data.to_csv(self.filename + ExportDataType.CSV.value)
        elif self.data_type == ExportDataType.EXCEL.value:
            self.data.to_excel(self.filename + ExportDataType.EXCEL.value)
        elif self.data_type == ExportDataType.HTML.value:
            self.data.to_html(self.filename + ExportDataType.HTML.value)
        elif self.data_type == ExportDataType.ZIP.value:
            self.data.to_pickle(self.filename + ExportDataType.ZIP.value)

    def run(self):
        self.export_file()
