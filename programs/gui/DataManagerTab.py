from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import (QComboBox, QFileDialog, QLabel, QMessageBox,
                             QProgressBar, QPushButton, QRadioButton,
                             QStatusBar, QTableWidget, QTableWidgetItem,
                             QWidget)

from DataManager import DataManager
from DataProcessor import DataProcessor
from HeatMapParameterWindow import HeatMapParameterWindow
from HelperFunctions import HelperFunction
from PlotDataObject import PlotDataObject

# TODO:
#  - do error checking
#  - show user what was selected
#  - convert npz to pandas DataFrame, then save data, if multiple time steps are
#    selected in heat map, save multiple files


class DataManagerTab(QWidget):
    is_data_selected = pyqtSignal(bool)

    def __init__(self, tab):
        super().__init__()

        self.title = 'Data Manager'
        self.source_directory = ""
        self.destination_directory = ""

        self.thread = None
        self.popup_window = None
        self.data_manager = None

        self.button_width = tab.button_width
        self.element_height = tab.element_height
        self.margin = tab.margin
        self.empty_label_width = tab.parent.width - 3 * self.margin
        self.height = tab.parent.height

        self.plot_data_object = None

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

        # source directory label and message box
        text = "Destination Directory Path"
        self.destination_directory_info_label = QLabel(self)
        self.destination_directory_info_label.setText(text)
        self.destination_directory_info_label.setGeometry(
            self.margin, 10 + 3.5 * self.element_height,
            HelperFunction.get_qt_text_width(self.destination_directory_info_label,
                                             text), self.element_height)

        text = "No Destination Directory Selected"
        self.destination_directory_label = QLabel(self)
        self.destination_directory_label.setText(text)
        self.destination_directory_label.setGeometry(self.margin,
                                                10 + 4.5 * self.element_height,
                                                self.empty_label_width,
                                                self.element_height)

        text = "Select Destination Directory"
        self.destination_directory_button = QPushButton(text, self)
        self.destination_directory_button.clicked.connect(
            self.show_destination_directory_dialog)
        self.destination_directory_button.setGeometry(
            self.margin, 10 + 5.75 * self.element_height, self.button_width,
            self.element_height)

        text = "Variable: Name"
        self.name_label = QLabel(self)
        self.name_label.setText(text)
        self.name_label.setGeometry(self.margin,
                                    10 + 7 * self.element_height,
                                    self.empty_label_width,
                                    self.element_height)

        text = "Name: Long Name"
        self.long_name_label = QLabel(self)
        self.long_name_label.setText(text)
        self.long_name_label.setGeometry(self.margin,
                                         10 + 8 * self.element_height,
                                         self.empty_label_width,
                                         self.element_height)

        text = "Units: Units"
        self.unit_label = QLabel(self)
        self.unit_label.setText(text)
        self.unit_label.setGeometry(self.margin,
                                    10 + 9 * self.element_height,
                                    self.empty_label_width,
                                    self.element_height)

        text = "Time Series Data"
        self.time_series_radio_button = QRadioButton(text, self)
        self.time_series_radio_button.setGeometry(
            self.margin, 10 + 10.25 * self.element_height, self.button_width,
            self.element_height)

        text = "Heat Map Data"
        self.heat_map_radio_button = QRadioButton(text, self)
        self.heat_map_radio_button.clicked.connect(
            self.export_data)
        self.heat_map_radio_button.setGeometry(
            self.button_width,
            10 + 10.25 * self.element_height, self.button_width,
            self.element_height)
        self.heat_map_radio_button.toggled.connect(
            self.update_table_on_button_toggle)

        self.table = QTableWidget(self)
        self.table.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setRowCount(5)
        self.table.setColumnCount(6)

        header_list = [
            "Parameter", "Unit", "Minimum Value", "Maximum Value",
            "Selected Min Value", "Selected Max Value"
        ]
        for row in range(5):
            for col in range(6):
                if row == 0:
                    item = QTableWidgetItem(header_list[col])
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    self.table.setItem(row, col, item)
                elif col < 4:
                    item = QTableWidgetItem()
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    self.table.setItem(row, col, item)
                else:
                    item = QTableWidgetItem()
                    self.table.setItem(row, col, item)
        self.table.item(1, 0).setText("Time Range")
        self.table.item(2, 0).setText("Latitude Range")
        self.table.item(3, 0).setText("Longitude Range")
        self.table.item(4, 0).setText("Level Range")
        self.table.item(1, 1).setText("Date Hours")

        self.table.move(self.margin, 10 + 11.75 * self.element_height)
        self.resize_table()

        text = "Plot Data"
        self.plot_data_button = QPushButton(text, self)
        self.plot_data_button.clicked.connect(self.plot_data)
        self.plot_data_button.setGeometry(self.margin,
                                            10 + 18.25 * self.element_height,
                                            self.button_width,
                                            self.element_height)

        text = "Export Data"
        self.export_data_button = QPushButton(text, self)
        self.export_data_button.clicked.connect(self.export_data)
        self.export_data_button.setGeometry(2 * self.margin + self.button_width,
                                            10 + 18.25 * self.element_height,
                                            self.button_width,
                                            self.element_height)

        self.statusBar = QStatusBar(self)
        self.statusBar.setGeometry(0.5 * self.margin,
                                   self.height - 4 * self.margin,
                                   self.empty_label_width, self.element_height)
        self.statusBar.showMessage('Ready')

        self.time_series_radio_button.toggled.connect(
            self.update_table_on_button_toggle)
        self.time_series_radio_button.setChecked(True)

        self.show()

    def resize_table(self):
        self.table.resizeColumnsToContents()
        self.table.setFixedWidth(1.02 * self.table.columnWidth(0) +
                                       self.table.columnWidth(1) +
                                       self.table.columnWidth(2) +
                                       self.table.columnWidth(3) +
                                       self.table.columnWidth(4) +
                                       self.table.columnWidth(5))
        self.table.setFixedHeight(1.07 * self.table.rowHeight(0) +
                                        self.table.rowHeight(1) +
                                        self.table.rowHeight(2) +
                                        self.table.rowHeight(3) +
                                        self.table.rowHeight(4))

    def update_table_on_button_toggle(self):
        if self.time_series_radio_button.isChecked():
            self.table.item(2, 5).setFlags(Qt.ItemIsSelectable)
            self.table.item(2, 5).setText("------")
            self.table.item(3, 5).setFlags(Qt.ItemIsSelectable)
            self.table.item(3, 5).setText("------")
        else:
            self.table.item(
                2, 5).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable
                               | Qt.ItemIsEnabled)
            self.table.item(2, 5).setText("")
            self.table.item(
                3, 5).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable
                               | Qt.ItemIsEnabled)
            self.table.item(3, 5).setText("")

    def export_data(self):
        self.is_data_selected.emit(True)
        pass

    def plot_data(self):
        self.is_data_selected.emit(True)
        pass

    def update_info(self):
        text = "Variable: " + self.plot_data_object.data_info['name']
        self.name_label.setText(text)

        text = "Name: " + self.plot_data_object.data_info['long_name']
        self.long_name_label.setText(text)

        text = "Units: " + self.plot_data_object.data_info['units']
        self.unit_label.setText(text)

        data = self.plot_data_object.get_data_time_range_str()
        self.table.item(1, 2).setText(data[0])
        self.table.item(1, 3).setText(data[1])

        data = self.plot_data_object.get_data_lat_range_str()
        self.table.item(2, 2).setText(data[0])
        self.table.item(2, 1).setText(data[2])
        self.table.item(2, 3).setText(data[1])

        data = self.plot_data_object.get_data_lon_range_str()
        self.table.item(3, 2).setText(data[0])
        self.table.item(3, 1).setText(data[2])
        self.table.item(3, 3).setText(data[1])

        data = self.plot_data_object.get_data_lev_range_str()
        self.table.item(4, 2).setText(data[0])
        self.table.item(4, 1).setText(data[2])
        self.table.item(4, 3).setText(data[1])

        self.resize_table()

    def get_info(self):
        self.being_date = self.popup_window.begin_date
        self.end_date = self.popup_window.end_date
        self.export_format = self.popup_window.export_data_type
        self.level = self.popup_window.level

    @pyqtSlot(float)
    def update_progress_bar(self, progress: float):
        self.progressBar.setValue(progress)

    def stop_thread(self):
        if isinstance(self.thread, DataProcessor):
            self.thread.stop()

    def show_error(self, msg: str):
        error = QMessageBox(self)
        error.setWindowTitle("Error!")
        error.setText(msg)
        error.exec_()

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
        else:
            error = QMessageBox(self)
            error.setWindowTitle("Error!")
            error.setText("Directory Selection Failed!")
            error.exec_()

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

                self.plot_data_object = PlotDataObject(self.source_directory)
                self.data_manager = DataManager(self.source_directory,
                                                self.plot_data_object)

                self.update_info()
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

    # TODO: implement this
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
