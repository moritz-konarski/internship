from PyQt5.QtWidgets import (QComboBox, QFileDialog, QProgressBar, QWidget)

from DataProcessor import DataProcessor
from HelperFunctions import HelperFunction as hf


class DataProcessorTab(QWidget):
    def __init__(self, tab_window):
        super().__init__()

        self.title = 'Data Processor'
        self.destination_directory = ""
        self.source_directory = ""

        self.long_variable_name = ""
        self.data_processor = None

        self.button_width = tab_window.button_width
        self.element_height = tab_window.element_height
        self.margin = tab_window.horizontal_margin
        self.empty_label_width = tab_window.main_gui.width - 3 * self.margin
        self.height = tab_window.main_gui.height

        self.init_ui()

    def init_ui(self):
        # source directory label and message box
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

        # combo box for variables
        text = "Variables Available for Extraction"
        hf.create_label(self, text, self.margin,
                        10 + 3.5 * self.element_height, self.element_height)

        self.variable_combobox = QComboBox(self)
        self.variable_combobox.setGeometry(self.margin,
                                           10 + 4.5 * self.element_height,
                                           self.button_width,
                                           self.element_height)
        self.variable_combobox.currentIndexChanged.connect(
            self.update_variable_info)

        text = "Full Variable Name"
        self.variable_combobox_info_label = hf.create_label_with_width(
            self, text, 2 * self.margin + self.button_width,
                        10 + 4.55 * self.element_height, self.empty_label_width,
            self.element_height)

        text = "Extract"
        self.extract_button = hf.create_button(self, text, self.margin,
                                               10 + 5.75 * self.element_height,
                                               self.button_width,
                                               self.element_height)
        self.extract_button.clicked.connect(self.extract)

        text = "Cancel Extraction"
        self.cancel_extraction_button = hf.create_button(
            self, text, 2 * self.margin + self.button_width,
                        10 + 5.75 * self.element_height, self.button_width,
            self.element_height)
        self.cancel_extraction_button.clicked.connect(self.stop_thread)

        self.disable_extract_button()

        text = "Accurate Progress: 0%"
        self.percent_label = hf.create_label_with_width(self, text, self.margin,
                                                        10 + 7 * self.element_height,
                                                        self.empty_label_width,
                                                        self.element_height)

        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(self.margin,
                                     10 + 8.25 * self.element_height,
                                     self.empty_label_width,
                                     self.element_height)

        text = "Ready"
        self.statusBar = hf.create_status_bar(self, text, 0.5 * self.margin,
                                              self.height - 5.2 * self.margin,
                                              self.empty_label_width,
                                              self.element_height)

        self.show()

    def update_progress_bar(self, progress: float):
        self.progressBar.setValue(progress)
        self.percent_label.setText(
            "Accurate Progress: " + str(hf.round_number(progress, 4)))

    def show_thread_error(self, message: str):
        hf.show_error_message(self, message)

    def enable_extract_button(self):
        self.extract_button.setEnabled(True)
        self.cancel_extraction_button.setEnabled(True)

    def disable_extract_button(self):
        self.extract_button.setEnabled(False)
        self.cancel_extraction_button.setEnabled(False)

    def set_status_bar(self, status: str):
        self.statusBar.showMessage(status)

    def stop_thread(self):
        if isinstance(self.data_processor, DataProcessor):
            self.data_processor.stop()
            self.data_processor = None

    def update_variable_info(self):
        if not self.variable_combobox.currentText(
        ) is None and not self.variable_combobox.currentText() == '':
            self.long_variable_name = hf.get_long_variable_name(
                self.source_directory, self.variable_combobox.currentText())
            self.variable_combobox_info_label.setText(self.long_variable_name)

    def extract(self):
        self.enable_extract_button()

        if self.show_destination_directory_dialog():
            self.data_processor = DataProcessor(self.source_directory,
                                                self.destination_directory,
                                                self.variable_combobox.currentText())
            self.data_processor.extraction_progress_update.connect(
                self.update_progress_bar)
            self.data_processor.finished.connect(self.enable_extract_button)
            self.data_processor.extraction_status_message.connect(
                self.set_status_bar)
            self.data_processor.error.connect(self.show_thread_error)
            self.data_processor.start()

    def show_source_directory_dialog(self):
        msg = "Select Source Directory"
        self.statusBar.showMessage(msg)
        file_name = QFileDialog.getExistingDirectory(self, msg)

        if file_name:
            if hf.is_valid_nc_source_directory(
                    file_name) and hf.can_read_directory(file_name):
                self.source_directory = file_name
                self.source_directory_label.setText(self.source_directory)
                self.variable_combobox.clear()
                self.variable_combobox.addItems(
                    hf.get_available_variables(self.source_directory))
                self.extract_button.setEnabled(True)
                self.statusBar.showMessage("Source Directory Selected")
            else:
                hf.show_error_message(
                    self, "The Directory is not a valid Source Directory!")
                return
        else:
            hf.show_error_message(self, "Directory Selection Failed!")
            return

    def show_destination_directory_dialog(self) -> bool:
        msg = "Select Destination Directory"
        self.statusBar.showMessage(msg)
        file_name = QFileDialog.getExistingDirectory(self, msg)

        if file_name:
            if hf.can_write_directory(file_name):
                self.destination_directory = file_name
                self.statusBar.showMessage("Destination Directory Selected")
                return True
            else:
                hf.show_error_message(self, "Directory Cannot Be Written To!")
                return False
        else:
            hf.show_error_message(self, "Directory Selection Failed!")
            return False
