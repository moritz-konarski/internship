from PyQt5.QtWidgets import (QStatusBar, QWidget, QLabel, QPushButton,
                             QProgressBar, QComboBox, QFileDialog, QMessageBox)
from PyQt5.QtCore import pyqtSlot
from DataProcessor import DataProcessor
from HelperFunctions import HelperFunction
from DataManager import DataManager
from HeatMapParameterWindow import HeatMapParameterWindow

# TODO:
#  - create input fields for min and max lat/lon
#  - do error checking
#  - get data from popups
#  - show user what was selected
#  - convert npz to pandas DataFrame, then save data


class DataManagerTab(QWidget):
    def __init__(self, tab):
        super().__init__()

        self.title = 'Data Manager'
        self.source_directory = ""

        self.long_variable_name = ""
        self.thread = None
        self.popup_window = None

        self.data_manager = None

        self.get_time_series_info_window = None
        self.get_heat_map_info_window = None

        self.button_width = tab.button_width
        self.element_height = tab.element_height
        self.margin = tab.margin
        self.empty_label_width = tab.parent.width - 3 * self.margin
        self.height = tab.parent.height

        self.being_date = None
        self.end_date = None
        self.level = None
        self.export_format = None
        self.lat_min = None
        self.lat_max = None
        self.lon_min = None
        self.lon_max = None

        # source directory label and message box
        text = "Source Directory Path"
        self.source_directory_info_label = QLabel(self)
        self.source_directory_info_label.setText(text)
        self.source_directory_info_label.setGeometry(
            self.margin, 10,
            HelperFunction.get_qt_text_width(self.source_directory_info_label,
                                             text), self.element_height)

        text = "No Source Directory Selected"
        self.source_directory_label = QLabel(self)
        self.source_directory_label.setText(text)
        self.source_directory_label.setGeometry(self.margin,
                                                10 + self.element_height,
                                                self.empty_label_width,
                                                self.element_height)

        text = "Select Source Directory"
        self.source_directory_button = QPushButton(text, self)
        self.source_directory_button.clicked.connect(
            self.show_source_directory_dialog)
        self.source_directory_button.setGeometry(
            self.margin, 10 + 2.25 * self.element_height, self.button_width,
            self.element_height)

        text = "Variable: Name"
        self.name_label = QLabel(self)
        self.name_label.setText(text)
        self.name_label.setGeometry(self.margin, 10 + 4 * self.element_height,
                                    self.empty_label_width,
                                    self.element_height)
        text = "Name: Long Name"
        self.long_name_label = QLabel(self)
        self.long_name_label.setText(text)
        self.long_name_label.setGeometry(self.margin,
                                         10 + 5 * self.element_height,
                                         self.empty_label_width,
                                         self.element_height)

        text = "Units: Units"
        self.unit_label = QLabel(self)
        self.unit_label.setText(text)
        self.unit_label.setGeometry(self.margin, 10 + 6 * self.element_height,
                                    self.empty_label_width,
                                    self.element_height)

        text = "Time Range: beginning to end"
        self.time_range_label = QLabel(self)
        self.time_range_label.setText(text)
        self.time_range_label.setGeometry(self.margin,
                                          10 + 7 * self.element_height,
                                          self.empty_label_width,
                                          self.element_height)

        text = "Latitude Range: lat range"
        self.lat_range_label = QLabel(self)
        self.lat_range_label.setText(text)
        self.lat_range_label.setGeometry(self.margin,
                                         10 + 8 * self.element_height,
                                         self.empty_label_width,
                                         self.element_height)

        text = "Longitude Range: lon range"
        self.lon_range_label = QLabel(self)
        self.lon_range_label.setText(text)
        self.lon_range_label.setGeometry(self.margin,
                                         10 + 9 * self.element_height,
                                         self.empty_label_width,
                                         self.element_height)

        text = "Levels: level count"
        self.level_range_label = QLabel(self)
        self.level_range_label.setText(text)
        self.level_range_label.setGeometry(self.margin,
                                           10 + 10 * self.element_height,
                                           self.empty_label_width,
                                           self.element_height)

        text = "Export Time Series Data"
        self.export_time_series_button = QPushButton(text, self)
        self.export_time_series_button.clicked.connect(
            self.export_time_series_data)
        self.export_time_series_button.setGeometry(
            self.margin, 10 + 11.5 * self.element_height, self.button_width,
            self.element_height)

        text = "Export Heat Map Data"
        self.export_heat_map_button = QPushButton(text, self)
        self.export_heat_map_button.clicked.connect(self.export_heat_map_data)
        self.export_heat_map_button.setGeometry(self.margin,
                                                10 + 13 * self.element_height,
                                                self.button_width,
                                                self.element_height)

        text = "Selected Time Range: beginning to end"
        self.selected_time_range_label = QLabel(self)
        self.selected_time_range_label.setText(text)
        self.selected_time_range_label.setGeometry(
            self.margin, 10 + 14.5 * self.element_height,
            self.empty_label_width, self.element_height)

        text = "Selected Latitude Range: lat range"
        self.selected_lat_range_label = QLabel(self)
        self.selected_lat_range_label.setText(text)
        self.selected_lat_range_label.setGeometry(
            self.margin, 10 + 15.5 * self.element_height,
            self.empty_label_width, self.element_height)

        text = "Selected Longitude Range: lon range"
        self.selected_lon_range_label = QLabel(self)
        self.selected_lon_range_label.setText(text)
        self.selected_lon_range_label.setGeometry(
            self.margin, 10 + 16.5 * self.element_height,
            self.empty_label_width, self.element_height)

        text = "Selected Level: level count"
        self.selected_level_range_label = QLabel(self)
        self.selected_level_range_label.setText(text)
        self.selected_level_range_label.setGeometry(
            self.margin, 10 + 17.5 * self.element_height,
            self.empty_label_width, self.element_height)

        self.show()

    def export_time_series_data(self):
        pass

    def export_heat_map_data(self):
        if isinstance(self.data_manager, DataManager):
            self.popup_window = HeatMapParameterWindow(
                self, self.data_manager.metadata['name'],
                self.data_manager.begin_datetime,
                self.data_manager.end_datetime, self.data_manager.level_count,
                self.data_manager.lat_min, self.data_manager.lat_min,
                self.data_manager.lon_min, self.data_manager.lon_max)
            self.popup_window.info_submitted.connect(self.get_heat_map_info)

    def update_info_labels(self):
        text = "Variable: " + self.data_manager.metadata['name']
        self.name_label.setText(text)
        text = "Name: " + self.data_manager.metadata['long_name']
        self.long_name_label.setText(text)
        text = "Units: " + self.data_manager.metadata['units']
        self.unit_label.setText(text)
        text = "Time Range: " + self.data_manager.metadata[
            'begin_date'] + " to " + self.data_manager.metadata['end_date']
        self.time_range_label.setText(text)
        text = "Latitude Range: " + str(
            self.data_manager.metadata['lat_min']) + " to " + str(
                self.data_manager.metadata['lat_max'])
        self.lat_range_label.setText(text)
        text = "Longitute Range: " + str(
            self.data_manager.metadata['lon_min']) + " to " + str(
                self.data_manager.metadata['lon_max'])
        self.lon_range_label.setText(text)
        text = "Levels: " + str(self.data_manager.metadata['lev_count'])
        self.level_range_label.setText(text)

    def get_heat_map_info(self):
        self.being_date = self.popup_window.begin_date
        self.end_date = self.popup_window.end_date
        self.export_format = self.popup_window.export_data_type
        self.level = self.popup_window.level
        #self.lat_min

    def lol(self):
        # destination directory label and message box
        text = "Destination Directory Path"
        self.destination_directory_info_label = QLabel(self)
        self.destination_directory_info_label.setText(text)
        self.destination_directory_info_label \
            .setGeometry(self.margin,
                         10 + 4 * self.element_height,
                         HelperFunction.get_qt_text_width(
                             self.destination_directory_info_label,
                             text),
                         self.element_height)

        self.destination_directory_label = QLabel(self)
        self.destination_directory_label.setText("No Directory Selected")
        self.destination_directory_label.setGeometry(
            self.margin, 10 + 5 * self.element_height, self.empty_label_width,
            self.element_height)

        text = "Select Destination Directory"
        self.destination_directory_button = QPushButton(text, self)
        self.destination_directory_button.clicked.connect(
            self.show_destination_directory_dialog)
        self.destination_directory_button.setGeometry(
            self.margin, 10 + 6.25 * self.element_height, self.button_width,
            self.element_height)

        # combo box for variables
        text = "Variables Available for Extraction"
        self.variable_combobox_info_label = QLabel(self)
        self.variable_combobox_info_label.setText(text)
        self.variable_combobox_info_label \
            .setGeometry(self.margin,
                         10 + 8 * self.element_height,
                         HelperFunction.get_qt_text_width(
                             self.variable_combobox_info_label,
                             text),
                         self.element_height)

        self.variable_combobox = QComboBox(self)
        self.variable_combobox.currentIndexChanged.connect(
            self.update_variable_info)
        self.variable_combobox.setGeometry(self.margin,
                                           10 + 9.25 * self.element_height,
                                           self.button_width,
                                           self.element_height)

        self.variable_combobox_info_label = QLabel(self)
        self.variable_combobox_info_label.setText("Full Variable Name")
        self.variable_combobox_info_label.setGeometry(
            2 * self.margin + self.button_width,
            10 + 9.3 * self.element_height, self.empty_label_width,
            self.element_height)

        # extract button
        self.extract_button = QPushButton("Extract", self)
        self.extract_button.setFixedHeight(self.element_height)
        self.extract_button.clicked.connect(self.extract)
        self.extract_button.setGeometry(self.margin,
                                        10 + 11.25 * self.element_height,
                                        self.button_width, self.element_height)
        self.disable_extract_button()

        # cancel extraction button
        self.cancel_extraction_button = QPushButton("Cancel Extraction", self)
        self.cancel_extraction_button.setFixedHeight(self.element_height)
        self.cancel_extraction_button.clicked.connect(self.stop_thread)
        self.cancel_extraction_button.setGeometry(
            2 * self.margin + self.button_width,
            10 + 11.25 * self.element_height, self.button_width,
            self.element_height)

        # create the progress bar
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(self.margin,
                                     10 + 13 * self.element_height,
                                     self.empty_label_width,
                                     self.element_height)

        self.statusBar = QStatusBar(self)
        self.statusBar.setGeometry(0.5 * self.margin,
                                   self.height - 4 * self.margin,
                                   self.empty_label_width, self.element_height)
        self.statusBar.showMessage('Ready')

        self.show()

    @pyqtSlot(float)
    def update_progress_bar(self, progress: float):
        self.progressBar.setValue(progress)

    def update_variable_info(self):
        if not self.variable_combobox.currentText(
        ) is None and not self.variable_combobox.currentText() == '':
            self.long_variable_name = \
                HelperFunction.get_long_variable_name(
                    self.source_directory, self.variable_combobox.currentText())
            self.variable_combobox_info_label.setText(self.long_variable_name)

    def stop_thread(self):
        if isinstance(self.thread, DataProcessor):
            self.thread.stop()

    def extract(self):
        self.enable_extract_button()

        if self.destination_directory == "":
            error = QMessageBox(self)
            error.setWindowTitle("Error!")
            error.setText("You must set a destination directory!")
            error.exec_()
            return

        self.thread = DataProcessor(self.source_directory,
                                    self.destination_directory,
                                    self.variable_combobox.currentText())
        self.thread.extraction_progress_update.connect(
            self.update_progress_bar)
        self.thread.finished.connect(self.enable_extract_button)
        self.thread.extraction_status_message.connect(self.set_status_bar)
        self.thread.error.connect(self.show_error)
        self.thread.start()

    def show_error(self, msg: str):
        error = QMessageBox(self)
        error.setWindowTitle("Error!")
        error.setText(msg)
        error.exec_()

    def enable_extract_button(self):
        self.extract_button.setEnabled(True)

    def disable_extract_button(self):
        self.extract_button.setEnabled(False)

    def set_status_bar(self, status: str):
        self.statusBar.showMessage(status)

    def show_destination_directory_dialog(self):
        msg = "Select Destination Directory"
        self.statusBar.showMessage(msg)
        file_name = QFileDialog.getExistingDirectory(self, msg)

        if file_name:
            if HelperFunction.can_write_directory(file_name):
                self.destination_directory = file_name
                self.destination_directory_label.setText(
                    self.destination_directory)
                self.statusBar.showMessage("Destination Directory Selected")
            else:
                error = QMessageBox(self)
                error.setWindowTitle("Error!")
                error.setText("Directory Cannot Be Written To!")
                error.exec_()
                return
        else:
            error = QMessageBox(self)
            error.setWindowTitle("Error!")
            error.setText("Directory Selection Failed!")
            error.exec_()
            return

    def show_source_directory_dialog(self):
        msg = "Select Source Directory"
        # self.statusBar.showMessage(msg)
        file_name = QFileDialog.getExistingDirectory(self, msg)

        if file_name:
            if HelperFunction.is_valid_npz_source_directory(
                    file_name) and HelperFunction.can_read_directory(
                        file_name):
                self.source_directory = file_name
                self.source_directory_label.setText(self.source_directory)

                self.data_manager = DataManager(self.source_directory)

                self.update_info_labels()

                # self.variable_combobox.clear()
                # self.variable_combobox.addItems(
                #    HelperFunction.get_available_variables(
                #        self.source_directory))
                # self.extract_button.setEnabled(True)
                # self.statusBar.showMessage("Source Directory Selected")
            else:
                error = QMessageBox(self)
                error.setWindowTitle("Error!")
                error.setText("The Directory is not a valid Source Directory!")
                error.exec_()
                return
        else:
            error = QMessageBox(self)
            error.setWindowTitle("Error!")
            error.setText("Directory Selection Failed!")
            error.exec_()
            return

    def find_lat_or_lon_index(self, given: str) -> int:
        val = float(given)
        min = np.nanmin(options)
        max = np.nanmax(options)

        if val > max or val < min:
            print("Latitute or Longitute out of range")
            exit(-1)

        best_index = -1
        min_diff = max
        for (i, opt) in enumerate(options):
            if abs(opt - val) < min_diff:
                best_index = i

        return best_index
