import os
from PyQt5.QtWidgets import (QFileDialog, QMessageBox, QWidget, QProgressBar, QComboBox)

from DataManager import DataManager
from DataPlotter import DataPlotter
from HelperFunctions import HelperFunction as hf, PlotDataType


# TODO:
#  - convert npz to pandas DataFrames and then pass them to the export or plotting functions


class DataPlotTab(QWidget):
    def __init__(self, tab):
        super().__init__()

        self.title = 'Plot Data'
        self.destination_directory = ""
        self.data_manager = None

        self.dialog_box = None

        self.data_plotter = None

        self.button_width = tab.button_width
        self.element_height = tab.element_height
        self.margin = tab.horizontal_margin
        self.empty_label_width = tab.main_gui.width - 3 * self.margin
        self.height = tab.main_gui.height
        self.export_data_type = None

        self.init_ui()

        self.set_buttons_enabled(True)


    def init_ui(self):
        text = "Plot"
        self.export_button = hf.create_button(self, text, self.margin,
                                              10 + 2.25 * self.element_height,
                                              self.button_width,
                                              self.element_height)
        self.export_button.clicked.connect(self.export)

        text = "Plot File Type"
        hf.create_label(self, text, self.margin,
                        10, self.element_height)

        self.export_combobox = QComboBox(self)
        self.export_combobox.setGeometry(self.margin,
                                         10 + 1 * self.element_height,
                                         self.button_width,
                                         self.element_height)
        self.export_combobox.addItems([x.value for x in PlotDataType])

        text = "Cancel Plotting"
        self.cancel_export_button = hf.create_button(
            self, text, 2 * self.margin + self.button_width,
                        10 + 2.25 * self.element_height, self.button_width,
            self.element_height)
        self.cancel_export_button.clicked.connect(self.stop_thread)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(self.margin, 10 + 3.5 * self.element_height,
                                      self.empty_label_width,
                                      self.element_height)

        self.status_bar = hf.create_status_bar(self, "Ready", 0.5 * self.margin,
                                               self.height - 4 * self.margin,
                                               self.empty_label_width,
                                               self.element_height)

        self.show()

    def stop_thread(self):
        self.data_plotter.stop()
        self.status_bar.showMessage("Plotting Cancelled")
        self.progress_bar.setValue(0)

    def set_data_manager(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.progress_bar.setValue(0)
        self.set_buttons_enabled(True)
        self.status_bar.showMessage("Ready")

    def update_progress_bar(self, value: float):
        print("updated bar: " + str(value))
        self.progress_bar.setValue(value)

    def export(self):
        message_box = QMessageBox(self)
        answer = message_box.question(self, 'Attention', "This action will generate " + str(self.data_manager.total_files) + " files. Proceed?",
                                      message_box.Yes | message_box.No)
        if answer == message_box.Yes:
            print("plot started")
            self.dialog_box = None
            self.set_buttons_enabled(False)
            if self.show_destination_directory_dialog():

                self.destination_directory = self.destination_directory + self.data_manager.var_name + "-plotted" \
                                             + hf.get_dir_separator()

                os.makedirs(self.destination_directory, exist_ok=True)
                self.status_bar.showMessage("Plotting...")
                if not self.data_manager.is_iterator_prepared:
                    self.data_manager.prepare_data_iterator()
                self.data_manager.data_progress.connect(self.update_progress_bar)
                self.data_plotter = DataPlotter(self.data_manager)
                self.data_plotter.set_attributes(
                    self.export_combobox.currentText(), self.destination_directory)
                self.data_plotter.finished.connect(self.export_finished)
                self.data_plotter.start()
            return
        else:
            return

    def export_finished(self):
        self.status_bar.showMessage("Finished!")
        self.set_buttons_enabled(True)

    def set_buttons_enabled(self, enabled: bool):
        self.export_button.setEnabled(enabled)
        self.cancel_export_button.setDisabled(enabled)

    def show_destination_directory_dialog(self) -> bool:
        msg = "Select Destination Directory"
        self.status_bar.showMessage(msg)
        file_name = QFileDialog.getExistingDirectory(self, msg)

        if file_name:
            if hf.can_write_directory(file_name):
                self.destination_directory = hf.format_directory_path(file_name)
                self.status_bar.showMessage("Destination Directory Selected")
                return True
            else:
                hf.show_error_message(self, "Directory Cannot Be Written To!")
                return False
        else:
            hf.show_error_message(self, "Directory Selection Failed!")
            return False
