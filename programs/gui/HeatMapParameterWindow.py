import datetime

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QComboBox,
                             QDateTimeEdit, QDesktopWidget, QLineEdit)

from HelperFunctions import HelperFunction, ExportDataType


class HeatMapParameterWindow(QWidget):
    info_submitted = pyqtSignal()

    def __init__(self, parent, var_name: str, begin_date: datetime,
                 end_date: datetime, level_count: int, lat_min: float,
                 lat_max: float, lon_min: float, lon_max: float):
        super().__init__()

        self.title = 'Heat Map Parameters'
        self.setWindowTitle(self.title)

        self.margin = parent.margin
        self.element_height = parent.element_height

        self.button_width = parent.button_width
        self.begin_date = begin_date
        self.level = level_count
        self.end_date = end_date
        self.file_name = var_name
        self.export_data_type = ExportDataType.CSV
        self.lon_min = lon_min
        self.lon_max = lon_max
        self.lat_min = lat_min
        self.lat_max = lat_max

        text = "Choose Start Date and Time"
        self.begin_date_edit_label = QLabel(self)
        self.begin_date_edit_label.setText(text)
        self.begin_date_edit_label \
            .setGeometry(self.margin,
                         10,
                         HelperFunction.get_qt_text_width(
                             self.begin_date_edit_label,
                             text),
                         self.element_height)
        self.begin_date_edit = QDateTimeEdit(self, calendarPopup=True)
        self.begin_date_edit.setDateTime(self.begin_date)
        self.begin_date_edit.setGeometry(self.margin, 10 + self.element_height,
                                         200, self.element_height)

        text = "Choose End Date and Time"
        self.end_date_edit_label = QLabel(self)
        self.end_date_edit_label.setText(text)
        self.end_date_edit_label \
            .setGeometry(self.margin,
                         10 + 2 * self.element_height,
                         HelperFunction.get_qt_text_width(
                             self.end_date_edit_label,
                             text),
                         self.element_height)
        self.end_date_edit = QDateTimeEdit(self, calendarPopup=True)
        self.end_date_edit.setDateTime(self.end_date)
        self.end_date_edit.setGeometry(self.margin,
                                       10 + 3 * self.element_height, 200,
                                       self.element_height)

        text = "Data Formats for Exporting"
        self.export_data_type_combobox_label = QLabel(self)
        self.export_data_type_combobox_label.setText(text)
        self.export_data_type_combobox_label \
            .setGeometry(self.margin,
                         10 + 4 * self.element_height,
                         HelperFunction.get_qt_text_width(
                             self.export_data_type_combobox_label,
                             text),
                         self.element_height)

        self.export_data_type_combobox = QComboBox(self)
        self.export_data_type_combobox.addItems(
            [part.value for part in ExportDataType])
        self.export_data_type_combobox.setGeometry(
            self.margin, 10 + 5 * self.element_height, self.button_width,
            self.element_height)

        self.level_text_box = None
        self.level_text_box_label = None
        if level_count != 0:
            text = "Choose Level to Export"
            self.level_text_box_label = QLabel(self)
            self.level_text_box_label.setText(text)
            self.level_text_box_label \
                .setGeometry(self.margin,
                             10 + 6 * self.element_height,
                             HelperFunction.get_qt_text_width(
                                 self.level_text_box_label,
                                 text),
                             self.element_height)

            self.level_text_box = QLineEdit(self)
            self.level_text_box.setText(str(level_count))
            self.level_text_box.setGeometry(self.margin,
                                            10 + 7 * self.element_height,
                                            self.button_width,
                                            self.element_height)

        text = "Set Parameters"
        self.submit_button = QPushButton(text, self)
        self.submit_button.clicked.connect(self.close_popup)
        self.submit_button.setGeometry(self.margin,
                                       10 + 8.5 * self.element_height,
                                       self.button_width, self.element_height)

        self.setGeometry(0, 0, self.button_width + 2 * self.margin,
                         10 + 18 * self.element_height)
        self.center_window()
        self.show()

    def close_popup(self):
        self.export_data_type = self.export_data_type_combobox.currentText()
        self.begin_date = self.begin_date_edit.dateTime()
        self.end_date = self.end_date_edit.dateTime()
        if isinstance(self.level_text_box, QLineEdit):
            self.level = int(self.level_text_box.text())
        else:
            self.level = 0
        self.hide()
        self.info_submitted.emit()

    def is_info_set(self):
        return self.info_set

    def center_window(self):
        frame_geometry = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
