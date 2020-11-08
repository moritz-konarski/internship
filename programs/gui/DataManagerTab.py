from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QFileDialog, QTableWidget, QTableWidgetItem,
                             QWidget)

from DataManager import DataManager
from HelperFunctions import HelperFunction as hf, PlotType, DataAction


# TODO:
#  - convert npz to pandas DataFrames and then pass them to the export or plotting functions


class DataManagerTab(QWidget):
    data_selection_signal = pyqtSignal(bool, DataAction)

    def __init__(self, tab):
        super().__init__()

        self.title = 'Data Manager'
        self.source_directory = ""

        self.thread = None
        self.popup = None
        self.data_manager = None

        self.button_width = tab.button_width
        self.element_height = tab.element_height
        self.margin = tab.horizontal_margin
        self.empty_label_width = tab.main_gui.width - 3 * self.margin
        self.height = tab.main_gui.height

        self.data_has_level = True

        self.is_updating = False

        self.data_action = None
        self.plot_type = None

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
        hf.create_label(self, text, self.margin,
                        10 + 7.75 * self.element_height, self.element_height)

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

        text = "Export Data"
        self.export_data_button = hf.create_button(
            self, text, self.margin, 10 + 15.75 * self.element_height,
            self.button_width, self.element_height)

        text = "Plot Data"
        self.plot_data_button = hf.create_button(
            self, text, 2 * self.margin + self.button_width,
                        10 + 15.75 * self.element_height, self.button_width,
            self.element_height)
        self.plot_data_button.clicked.connect(self.plot_data)

        self.export_data_button.clicked.connect(self.export_data)

        self.time_series_radio_button.toggled.connect(
            self.update_table_on_button_toggle)
        self.time_series_radio_button.setChecked(True)

        self.statusBar = hf.create_status_bar(self, "Ready", 0.5 * self.margin,
                                              self.height - 4 * self.margin,
                                              self.empty_label_width,
                                              self.element_height)

        self.show()

    def get_data_manager(self) -> DataManager:
        return self.data_manager

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
        if self.heat_map_radio_button.isChecked():
            self.plot_type = PlotType.HEAT_MAP
        else:
            self.plot_type = PlotType.TIME_SERIES

        self.is_updating = True
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

        self.is_updating = False

    def check_data_bounds(self):
        if not self.is_updating and isinstance(self.data_manager, DataManager):
            row = self.table.currentRow()
            col = self.table.currentColumn()
            if not self.is_cell_empty(row, col):
                if row == 1 and col == 4:
                    if self.data_manager.set_begin_time(
                            self.table.item(row, col).text()):
                        self.table.item(row, col).setText(
                            hf.get_str_from_datetime(
                                self.data_manager.begin_date))
                if row == 1 and col == 5:
                    if self.data_manager.set_end_time(
                            self.table.item(row, col).text()):
                        self.table.item(row, col).setText(
                            hf.get_str_from_datetime(
                                self.data_manager.end_date))
                if row == 2 and col == 4:
                    if self.data_manager.set_lat_min(
                            self.table.item(row, col).text()):
                        self.table.item(row, col).setText(
                            str(self.data_manager.lat_min))
                if row == 2 and col == 5:
                    if self.data_manager.set_lat_max(
                            self.table.item(row, col).text()):
                        self.table.item(row, col).setText(
                            str(self.data_manager.lat_max))
                if row == 3 and col == 4:
                    if self.data_manager.set_lon_min(
                            self.table.item(row, col).text()):
                        self.table.item(row, col).setText(
                            str(self.data_manager.lon_min))
                if row == 3 and col == 5:
                    if self.data_manager.set_lon_max(
                            self.table.item(row, col).text()):
                        self.table.item(row, col).setText(
                            str(self.data_manager.lon_max))
                if row == 4 and col == 4:
                    if self.data_manager.set_lev_min(
                            self.table.item(row, col).text()):
                        self.table.item(row, col).setText(
                            str(hf.round_number(self.data_manager.lev_min, 5)))
                if row == 4 and col == 5:
                    if self.data_manager.set_lev_max(
                            self.table.item(row, col).text()):
                        self.table.item(row, col).setText(
                            str(hf.round_number(self.data_manager.lev_max, 5)))

    def check_data_bounds_on_button_press(self):
        if self.plot_type == PlotType.TIME_SERIES:
            if not self.is_updating and isinstance(self.data_manager,
                                                   DataManager):
                b1 = self.data_manager.set_begin_time(
                    self.table.item(1, 4).text())
                b2 = self.data_manager.set_end_time(
                    self.table.item(1, 5).text())
                b3 = self.data_manager.set_lat_min(
                    self.table.item(2, 4).text())
                b4 = self.data_manager.set_lon_min(
                    self.table.item(3, 4).text())
                if len(self.data_manager.shape) == 4:
                    b5 = self.data_manager.set_lev_min(
                        self.table.item(4, 4).text())
                    b6 = self.data_manager.set_lev_max(
                        self.table.item(4, 5).text())
                    if b1 and b2 and b3 and b4 and b5 and b6:
                        if self.data_manager.begin_date < self.data_manager.end_date:
                            return True
                        else:
                            hf.show_error_message(
                                self, "Please select a non-zero time range!")
                            return False
                    else:
                        return False
                else:
                    if b1 and b2 and b3 and b4:
                        if self.data_manager.begin_date < self.data_manager.end_date:
                            return True
                        else:
                            hf.show_error_message(
                                self, "Please select a non-zero time range!")
                            return False
                    else:
                        return False
            else:
                hf.show_error_message(self, "Select a source file!")
                return False
        elif self.plot_type == PlotType.HEAT_MAP:
            if not self.is_updating and isinstance(self.data_manager,
                                                   DataManager):
                b1 = self.data_manager.set_begin_time(
                    self.table.item(1, 4).text())
                b2 = self.data_manager.set_end_time(
                    self.table.item(1, 5).text())
                b3 = self.data_manager.set_lat_min(
                    self.table.item(2, 4).text())
                b4 = self.data_manager.set_lat_max(
                    self.table.item(2, 5).text())
                b5 = self.data_manager.set_lon_min(
                    self.table.item(3, 4).text())
                b6 = self.data_manager.set_lon_max(
                    self.table.item(3, 5).text())
                if len(self.data_manager.shape) == 4:
                    b7 = self.data_manager.set_lev_min(
                        self.table.item(4, 4).text())
                    b8 = self.data_manager.set_lev_max(
                        self.table.item(4, 5).text())
                    if b1 and b2 and b3 and b4 and b5 and b6 and b7 and b8:
                        return True
                    else:
                        return False
                else:
                    if b1 and b2 and b3 and b4 and b5 and b6:
                        return True
                    else:
                        return False
            else:
                hf.show_error_message(self, "Select a source file!")
                return False
        else:
            return False

    def show_error(self, message: str):
        hf.show_error_message(self, message)

    def clear_table(self):
        for row in range(1, 5):
            for col in range(4, 6):
                self.table.item(row, col).setText("")
        self.update_table_on_button_toggle()

    def export_data(self):
        if self.check_data_bounds_on_button_press():
            self.data_manager.set_data_action(self.data_action)
            self.data_manager.set_plot_type(self.plot_type)
            # self.popup = PrepareDataPopup(self)
            # self.popup.start()
            self.data_manager.preparation_finished.connect(
                self.export_data_signal)
            self.data_manager.message.connect(self.show_status_bar_message)
            self.data_manager.start()
            # self.data_selection_signal.emit(True, DataAction.EXPORT)
        else:
            hf.show_error_message(self, "Could not start Extraction!")
            return

    def plot_data(self):
        if self.check_data_bounds_on_button_press():
            self.data_manager.set_data_action(self.data_action)
            self.data_manager.set_plot_type(self.plot_type)
            # self.popup = PrepareDataPopup(self)
            # self.popup.start()
            self.data_manager.preparation_finished.connect(
                self.plot_data_signal)
            self.data_manager.message.connect(self.show_status_bar_message)
            self.data_manager.start()
            # self.data_selection_signal.emit(True, DataAction.PLOT)
        else:
            return

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
            self.table.item(4,
                            0).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table.item(4,
                            1).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table.item(4,
                            2).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table.item(4,
                            3).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table.item(4,
                            4).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable
                                        | Qt.ItemIsEnabled)
            self.table.item(4, 4).setText("")
            self.table.item(4,
                            5).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable
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

    def is_cell_empty(self, row: int, col: int) -> bool:
        if not self.table.item(row, col) is None:
            return self.table.item(row, col).text() == "" or self.table.item(
                row, col).text() == "------"
        return False

    def show_status_bar_message(self, string: str):
        self.statusBar.showMessage(string)

    def export_data_signal(self):
        self.data_selection_signal.emit(True, DataAction.EXPORT)

    def plot_data_signal(self):
        self.data_selection_signal.emit(True, DataAction.PLOT)

    def show_source_directory_dialog(self):
        msg = "Select Source Directory"
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
                hf.show_error_message(
                    self, "The Directory is not a valid Source Directory!")
                return
        else:
            hf.show_error_message(self, "Directory Selection Failed!")
            return
