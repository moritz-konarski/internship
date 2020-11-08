from PyQt5.QtWidgets import (QFileDialog, QWidget, QProgressBar, QComboBox)

from DataManager import DataManager
from ExportData import ExportData
from HelperFunctions import HelperFunction as hf, ExportDataType
from DataObject import DataObject


# TODO:
#  - convert npz to pandas DataFrames and then pass them to the export or plotting functions


class ExportDataTab(QWidget):
    def __init__(self, tab):
        super().__init__()

        self.title = 'Export Data'
        self.destination_directory = ""
        self.data_manager = None

        self.data_exporter = ExportData()

        self.button_width = tab.button_width
        self.element_height = tab.element_height
        self.margin = tab.horizontal_margin
        self.empty_label_width = tab.main_gui.width - 3 * self.margin
        self.height = tab.main_gui.height
        self.export_data_type = None

        self.init_ui()

    def init_ui(self):
        text = "Export"
        self.export_button = hf.create_button(self, text, self.margin,
                                              10 + 5.75 * self.element_height,
                                              self.button_width,
                                              self.element_height)
        self.export_button.clicked.connect(self.export)

        # combo box for variables
        text = "Export Data Types"
        hf.create_label(self, text, self.margin,
                        10 + 3.5 * self.element_height, self.element_height)

        self.export_combobox = QComboBox(self)
        self.export_combobox.setGeometry(self.margin,
                                         10 + 4.5 * self.element_height,
                                         self.button_width,
                                         self.element_height)
        self.export_combobox.addItems([x.value for x in ExportDataType])

        text = "Cancel Export"
        self.cancel_export_button = hf.create_button(
            self, text, 2 * self.margin + self.button_width,
                        10 + 5.75 * self.element_height, self.button_width,
            self.element_height)
        self.cancel_export_button.clicked.connect(self.stop_thread)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(self.margin, 10 + 7 * self.element_height,
                                      self.empty_label_width,
                                      self.element_height)

        self.status_bar = hf.create_status_bar(self, "Ready", 0.5 * self.margin,
                                               self.height - 4 * self.margin,
                                               self.empty_label_width, self.element_height)

        self.show()

    def stop_thread(self):
        pass

    def set_data_manager(self, data_manager: DataManager):
        self.data_manager = data_manager

    def update_progress_bar(self, value: float):
        self.progress_bar.setValue(value)

    def export(self):
        print("export started")
        if self.show_destination_directory_dialog():
            if not self.data_manager.is_iterator_prepared:
                self.data_manager.prepare_data_iterator()
            self.data_manager.data_progress.connect(self.update_progress_bar)
            for data_obj in iter(self.data_manager):
                print("in export tab iterator")
                self.data_exporter.set_attributes(data_obj,
                                                  self.export_combobox.currentText(),
                                                  self.destination_directory)


    def show_destination_directory_dialog(self) -> bool:
        msg = "Select Destination Directory"
        self.status_bar.showMessage(msg)
        file_name = QFileDialog.getExistingDirectory(self, msg)

        if file_name:
            if hf.can_write_directory(file_name):
                self.destination_directory = file_name
                self.status_bar.showMessage("Destination Directory Selected")
                return True
            else:
                hf.show_error_message(self, "Directory Cannot Be Written To!")
                return False
        else:
            hf.show_error_message(self, "Directory Selection Failed!")
            return False
