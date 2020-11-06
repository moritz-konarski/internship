from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import (QFileDialog, QLabel, QMessageBox, QPushButton,
                             QRadioButton, QStatusBar, QTableWidget,
                             QTableWidgetItem, QWidget)

from DataManager import DataManager
from DataProcessor import DataProcessor
from HelperFunctions import HelperFunction as hf
from enum import Enum, auto

# TODO:
#  - finish data input
#  - do error checking
#  - convert npz to pandas DataFrames and then pass them to the export or plotting functions


class DataAction(Enum):
    EXPORT = auto()
    PLOT = auto()


class DataManagerTab(QWidget):
    data_selection_signal = pyqtSignal(bool, DataAction)

    def __init__(self, tab):
        super().__init__()

        self.title = 'Data Manager'
        self.source_directory = ""

        self.thread = None
        self.data_manager = None

        self.button_width = tab.button_width
        self.element_height = tab.element_height
        self.margin = tab.horizontal_margin
        self.empty_label_width = tab.main_gui.width - 3 * self.margin
        self.height = tab.main_gui.height

        self.data_has_level = True

        self.init_ui()

    def init_ui(self):
        text = "Source Directory Path"
        hf.create_label(self, text, self.margin, 10, self.element_height)

        text = "No Source Directory Selected"
        self.source_directory_label = hf.create_label_with_width(
            self, text, self.margin, 10 + self.element_height,
            self.empty_label_width, self.element_height)

        text = "Select Source Directory"
        self.source_directory_button = hf.create_button(
            self, text, self.margin, 10 + 2.25 * self.element_height,
            self.button_width, self.element_height)
        self.source_directory_button.clicked.connect(
            self.show_source_directory_dialog)

        text = "Variable: Name"
        self.name_label = hf.create_label_with_width(
            self, text, self.margin, 10 + 3.5 * self.element_height,
            self.empty_label_width, self.element_height)

        text = "Name: Long Name"
        self.long_name_label = hf.create_label_with_width(
            self, text, self.margin, 10 + 4.5 * self.element_height,
            self.empty_label_width, self.element_height)

        text = "Units: Units"
        self.unit_label = hf.create_label_with_width(
            self, text, self.margin, 10 + 5.5 * self.element_height,
            self.empty_label_width, self.element_height)

        text = "Time Series Data"
        self.time_series_radio_button = hf.create_radio_button(
            self, text, self.margin, 10 + 6.75 * self.element_height,
            self.button_width, self.element_height)

        text = "Heat Map Data"
        self.heat_map_radio_button = hf.create_radio_button(
            self, text, self.button_width, 10 + 6.75 * self.element_height,
            self.button_width, self.element_height)

        self.heat_map_radio_button.toggled.connect(
            self.update_table_on_button_toggle)

        text = "Select data parameters here:"
        hf.create_label(self, text, self.margin, 10 + 7.75 * self.element_height, self.element_height)

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

        self.table.move(self.margin, 10 + 9 * self.element_height)
        self.resize_table()
        self.table.cellChanged.connect(self.check_data_bounds)

        text = "Plot Data"
        self.plot_data_button = hf.create_button(
            self, text, self.margin, 10 + 15.75 * self.element_height,
            self.button_width, self.element_height)
        self.plot_data_button.clicked.connect(self.plot_data)

        text = "Export Data"
        self.export_data_button = hf.create_button(
            self, text, 2 * self.margin + self.button_width,
            10 + 15.75 * self.element_height, self.button_width,
            self.element_height)

        self.export_data_button.clicked.connect(self.export_data)

        text = "Ready"
        self.statusBar = hf.create_status_bar(self, text, 0.5 * self.margin,
                                              self.height - 4 * self.margin,
                                              self.empty_label_width,
                                              self.element_height)

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
            self.table.item(2,
                            5).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable
                                        | Qt.ItemIsEnabled)
            self.table.item(2, 5).setText("")
            self.table.item(3,
                            5).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable
                                        | Qt.ItemIsEnabled)
            self.table.item(3, 5).setText("")

    def check_data_bounds(self):
        if isinstance(self.data_manager, DataManager):
            row = self.table.currentRow()
            col = self.table.currentColumn()
            if not self.is_cell_empty(row, col):
                if row == 1 and col == 4:
                    self.data_manager.set_begin_time(self.table.item(row, col).text())
                if row == 1 and col == 5:
                    self.data_manager.set_end_time(self.table.item(row, col).text())

    def show_error(self, message: str):
        hf.show_error_message(self, message)

    def clear_table(self):
        for row in range(1, 5):
            for col in range(4,6):
                self.table.item(row, col).setText("")
        self.update_table_on_button_toggle()

    def export_data(self):
        self.data_selection_signal.emit(True, DataAction.EXPORT)
        pass

    def plot_data(self):
        self.data_selection_signal.emit(True, DataAction.PLOT)
        pass

    def update_info(self):
        self.clear_table()
        text = "Variable: " + self.data_manager.metadata['name']
        self.name_label.setText(text)

        text = "Name: " + self.data_manager.metadata['long_name']
        self.long_name_label.setText(text)

        text = "Units: " + self.data_manager.metadata['units']
        self.unit_label.setText(text)

        data = self.data_manager.get_data_time_range_str()
        self.table.item(1, 2).setText(data[0])
        self.table.item(1, 3).setText(data[1])

        data = self.data_manager.get_data_lat_range_str()
        self.table.item(2, 2).setText(data[0])
        self.table.item(2, 1).setText(data[2])
        self.table.item(2, 3).setText(data[1])

        data = self.data_manager.get_data_lon_range_str()
        self.table.item(3, 2).setText(data[0])
        self.table.item(3, 1).setText(data[2])
        self.table.item(3, 3).setText(data[1])

        if self.data_has_level:
            self.table.item(4, 0).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable
                                        | Qt.ItemIsEnabled)
            self.table.item(4, 1).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable
                                        | Qt.ItemIsEnabled)
            self.table.item(4, 2).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable
                                        | Qt.ItemIsEnabled)
            self.table.item(4, 3).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable
                                        | Qt.ItemIsEnabled)
            self.table.item(4, 4).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable
                                        | Qt.ItemIsEnabled)
            self.table.item(4, 4).setText("")
            self.table.item(4, 5).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable
                                        | Qt.ItemIsEnabled)
            self.table.item(4, 5).setText("")

            data = self.data_manager.get_data_lev_range_str()
            self.table.item(4, 2).setText(data[0])
            self.table.item(4, 1).setText(data[2])
            self.table.item(4, 3).setText(data[1])
        else:
            self.table.item(4, 0).setFlags(Qt.ItemIsSelectable)
            self.table.item(4, 1).setFlags(Qt.ItemIsSelectable)
            self.table.item(4, 1).setText("------")
            self.table.item(4, 2).setFlags(Qt.ItemIsSelectable)
            self.table.item(4, 2).setText("------")
            self.table.item(4, 3).setFlags(Qt.ItemIsSelectable)
            self.table.item(4, 3).setText("------")
            self.table.item(4, 4).setFlags(Qt.ItemIsSelectable)
            self.table.item(4, 4).setText("------")
            self.table.item(4, 5).setFlags(Qt.ItemIsSelectable)
            self.table.item(4, 5).setText("------")

        self.resize_table()

    @pyqtSlot(float)
    def update_progress_bar(self, progress: float):
        self.progressBar.setValue(progress)

    def stop_thread(self):
        if isinstance(self.thread, DataProcessor):
            self.thread.stop()

    def set_status_bar(self, status: str):
        self.statusBar.showMessage(status)

    def is_cell_empty(self, row:int, col:int) -> bool:
        if not self.table.item(row, col) is None:
            return self.table.item(row, col).text() == ""
        return False

    def show_source_directory_dialog(self):
        msg = "Select Source Directory"
        # self.statusBar.showMessage(msg)
        file_name = QFileDialog.getExistingDirectory(self, msg)

        if file_name:
            if hf.is_valid_npz_source_directory(
                    file_name) and hf.can_read_directory(file_name):
                self.source_directory = file_name
                self.source_directory_label.setText(self.source_directory)

                self.data_manager = DataManager(self.source_directory)

                self.data_manager.error.connect(self.show_error)

                if len(self.data_manager.shape) == 4:
                    self.data_has_level = True
                else:
                    self.data_has_level = False 

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
