from PyQt5.QtWidgets import (QStatusBar, QWidget, QLabel, QPushButton,
                             QProgressBar, QComboBox, QFileDialog, QMessageBox,
                             QTableWidgetItem, QTableWidget, QRadioButton)
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5 import QtWidgets
from DataProcessor import DataProcessor
from HelperFunctions import HelperFunction
from DataManager import DataManager
from HeatMapParameterWindow import HeatMapParameterWindow
from PlotDataObject import PlotDataObject

# TODO:
#  - do error checking
#  - get data from popups
#  - show user what was selected
#  - convert npz to pandas DataFrame, then save data, if multiple time steps are
#    selected in heat map, save multiple files


class DataManagerTab(QWidget):
    def __init__(self, tab):
        super().__init__()

        self.title = 'Data Manager'
        self.source_directory = ""

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

        text = "Variable: Name"
        self.name_label = QLabel(self)
        self.name_label.setText(text)
        self.name_label.setGeometry(self.margin,
                                    10 + 3.5 * self.element_height,
                                    self.empty_label_width,
                                    self.element_height)

        text = "Name: Long Name"
        self.long_name_label = QLabel(self)
        self.long_name_label.setText(text)
        self.long_name_label.setGeometry(self.margin,
                                         10 + 4.5 * self.element_height,
                                         self.empty_label_width,
                                         self.element_height)

        text = "Units: Units"
        self.unit_label = QLabel(self)
        self.unit_label.setText(text)
        self.unit_label.setGeometry(self.margin,
                                    10 + 5.5 * self.element_height,
                                    self.empty_label_width,
                                    self.element_height)

        text = "Export Time Series Data"
        self.export_time_series_radio_button = QRadioButton(text, self)
        self.export_time_series_radio_button.setGeometry(
            self.margin, 10 + 6.75 * self.element_height, self.button_width,
            self.element_height)

        text = "Export Heat Map Data"
        self.export_heat_map_radio_button = QRadioButton(text, self)
        self.export_heat_map_radio_button.clicked.connect(
            self.export_data)
        self.export_heat_map_radio_button.setGeometry(
            2 * self.margin + self.button_width,
            10 + 6.75 * self.element_height, self.button_width,
            self.element_height)
        self.export_heat_map_radio_button.toggled.connect(
            self.update_table_on_button_toggle)

        self.tableWidget = QTableWidget(self)
        self.tableWidget.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setRowCount(5)
        self.tableWidget.setColumnCount(6)

        header_list = [
            "Parameter", "Unit", "Minimum Value", "Maximum Value",
            "Selected Min Value", "Selected Max Value"
        ]
        for row in range(5):
            for col in range(6):
                if row == 0:
                    item = QTableWidgetItem(header_list[col])
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    self.tableWidget.setItem(row, col, item)
                elif col < 4:
                    item = QTableWidgetItem()
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    self.tableWidget.setItem(row, col, item)
                else:
                    item = QTableWidgetItem()
                    self.tableWidget.setItem(row, col, item)
        self.tableWidget.item(1, 0).setText("Time Range")
        self.tableWidget.item(2, 0).setText("Latitude Range")
        self.tableWidget.item(3, 0).setText("Longitude Range")
        self.tableWidget.item(4, 0).setText("Level Range")
        self.tableWidget.item(1, 1).setText("Date Hours")

        self.tableWidget.move(self.margin, 10 + 8.25 * self.element_height)
        self.resize_table()

        text = "Export Data"
        self.export_data_button = QPushButton(text, self)
        self.export_data_button.clicked.connect(self.export_data)
        self.export_data_button.setGeometry(self.margin,
                                            10 + 14.75 * self.element_height,
                                            self.button_width,
                                            self.element_height)

        self.statusBar = QStatusBar(self)
        self.statusBar.setGeometry(0.5 * self.margin,
                                   self.height - 4 * self.margin,
                                   self.empty_label_width, self.element_height)
        self.statusBar.showMessage('Ready')

        self.export_time_series_radio_button.toggled.connect(
            self.update_table_on_button_toggle)
        self.export_time_series_radio_button.setChecked(True)

        self.show()

    def resize_table(self):
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.setFixedWidth(1.02 * self.tableWidget.columnWidth(0) +
                                       self.tableWidget.columnWidth(1) +
                                       self.tableWidget.columnWidth(2) +
                                       self.tableWidget.columnWidth(3) +
                                       self.tableWidget.columnWidth(4) +
                                       self.tableWidget.columnWidth(5))
        self.tableWidget.setFixedHeight(1.07 * self.tableWidget.rowHeight(0) +
                                        self.tableWidget.rowHeight(1) +
                                        self.tableWidget.rowHeight(2) +
                                        self.tableWidget.rowHeight(3) +
                                        self.tableWidget.rowHeight(4))

    def update_table_on_button_toggle(self):
        if self.export_time_series_radio_button.isChecked():
            self.tableWidget.item(2, 5).setFlags(Qt.ItemIsSelectable)
            self.tableWidget.item(2, 5).setText("------")
            self.tableWidget.item(3, 5).setFlags(Qt.ItemIsSelectable)
            self.tableWidget.item(3, 5).setText("------")
        else:
            self.tableWidget.item(
                2, 5).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable
                               | Qt.ItemIsEnabled)
            self.tableWidget.item(2, 5).setText("")
            self.tableWidget.item(
                3, 5).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable
                               | Qt.ItemIsEnabled)
            self.tableWidget.item(3, 5).setText("")

    def export_data(self):
        pass

    def update_info(self):
        text = "Variable: " + self.plot_data_object.data_info['name']
        self.name_label.setText(text)

        text = "Name: " + self.plot_data_object.data_info['long_name']
        self.long_name_label.setText(text)

        text = "Units: " + self.plot_data_object.data_info['units']
        self.unit_label.setText(text)

        data = self.plot_data_object.get_data_time_range_str()
        self.tableWidget.item(1, 2).setText(data[0])
        self.tableWidget.item(1, 3).setText(data[1])

        data = self.plot_data_object.get_data_lat_range_str()
        self.tableWidget.item(2, 2).setText(data[0])
        self.tableWidget.item(2, 1).setText(data[2])
        self.tableWidget.item(2, 3).setText(data[1])

        data = self.plot_data_object.get_data_lon_range_str()
        self.tableWidget.item(3, 2).setText(data[0])
        self.tableWidget.item(3, 1).setText(data[2])
        self.tableWidget.item(3, 3).setText(data[1])

        data = self.plot_data_object.get_data_lev_range_str()
        self.tableWidget.item(4, 2).setText(data[0])
        self.tableWidget.item(4, 1).setText(data[2])
        self.tableWidget.item(4, 3).setText(data[1])

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
