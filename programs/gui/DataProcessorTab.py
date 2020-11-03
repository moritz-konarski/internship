from PyQt5.QtWidgets import (QStatusBar, QWidget, QLabel, QPushButton,
                             QProgressBar, QComboBox, QFileDialog, QMessageBox)
from PyQt5.QtCore import pyqtSlot
from DataProcessor import DataProcessor
from HelperFunctions import HelperFunction


class DataProcessorTab(QWidget):
    def __init__(self, tab):
        super().__init__()

        self.title = 'Data Processor'
        self.destination_directory = ""
        self.source_directory = ""

        self.__src_dir_path = ""
        self.__dest_dir_path = ""
        self.__var_name_list = []
        self.__data_processor = None
        self.long_variable_name = ""
        self.thread = None

        self.button_width = tab.button_width
        self.element_height = tab.element_height
        self.margin = tab.margin
        self.empty_label_width = tab.parent.width - 3 * self.margin
        self.height = tab.parent.height

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

        # destination directory label and message box
        text = "Destination Directory Path"
        self.destination_directory_info_label = QLabel(self)
        self.destination_directory_info_label.setText(text)
        self.destination_directory_info_label \
            .setGeometry(self.margin,
                         10 + 4 * self.element_height,
                         HelperFunction.get_qt_text_width(self.destination_directory_info_label,
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
        self.statusBar.showMessage(msg)
        file_name = QFileDialog.getExistingDirectory(self, msg)

        if file_name:
            if HelperFunction.is_valid_source_directory(
                    file_name) and HelperFunction.can_read_directory(
                        file_name):
                self.source_directory = file_name
                self.source_directory_label.setText(self.source_directory)
                self.variable_combobox.clear()
                self.variable_combobox.addItems(
                    HelperFunction.get_available_variables(
                        self.source_directory))
                self.extract_button.setEnabled(True)
                self.statusBar.showMessage("Source Directory Selected")
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
