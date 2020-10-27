from DataProcessor import DataProcessor
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QDesktopWidget, QMainWindow, QPushButton,
                             QFileDialog, QComboBox, QProgressBar)
from PyQt5.QtCore import pyqtSlot


class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__init_ui()
        self.__src_dir_path = ""
        self.__dest_dir_path = ""
        self.__var_name_list = []
        self.__data_processor = None
        self.__long_variable_name = ""

    def __init_ui(self):
        scale_factor = 1.3
        font = self.font()
        font.setPointSize(11)
        window_width = 600

        # source directory label and message box
        self.__src_dir_title = QtWidgets.QLabel(self)
        self.__src_dir_title.setFont(font)

        text_height = self.__src_dir_title.fontMetrics().boundingRect(
            "0").height()
        button_height = 1.8 * text_height
        window_height = 16 * scale_factor * text_height

        self.__src_dir_title.setText("Source Directory Path")
        self.__src_dir_title.setFixedWidth(
            self.__src_dir_title.fontMetrics().boundingRect(255 * "0").width())
        self.__src_dir_title.move(20, 10)
        self.__src_dir_label = QtWidgets.QLabel(self)
        self.__src_dir_label.setFont(font)
        self.__src_dir_label.setText("--")
        self.__src_dir_label.setFixedWidth(
            self.__src_dir_label.fontMetrics().boundingRect(255 * "0").width())
        self.__src_dir_label.move(20, 10 + scale_factor * text_height)
        self.__src_dir_btn = QPushButton("Select Source Directory", self)
        self.__src_dir_btn.setFont(font)
        self.__src_dir_btn.setFixedWidth(
            1.1 * self.__src_dir_btn.fontMetrics().boundingRect(
                "Select Source Directory").width())
        self.__src_dir_btn.setFixedHeight(button_height)
        self.__src_dir_btn.clicked.connect(self.__show_src_dir_dialog)
        self.__src_dir_btn.move(20, 10 + 2.25 * scale_factor * text_height)

        # destination directory label and message box
        self.__dest_dir_title = QtWidgets.QLabel(self)
        self.__dest_dir_title.setFont(font)
        self.__dest_dir_title.setText("Destination Directory Path")
        self.__dest_dir_title.setFixedWidth(
            self.__src_dir_title.fontMetrics().boundingRect(255 * "0").width())
        self.__dest_dir_title.move(20, 10 + 4 * scale_factor * text_height)
        self.__dest_dir_label = QtWidgets.QLabel(self)
        self.__dest_dir_label.setFont(font)
        self.__dest_dir_label.setText("--")
        self.__dest_dir_label.setFixedWidth(
            self.__src_dir_label.fontMetrics().boundingRect(255 * "0").width())
        self.__dest_dir_label.move(20, 10 + 5 * scale_factor * text_height)
        self.__dest_dir_btn = QPushButton("Select Destination Directory", self)
        self.__dest_dir_btn.setFont(font)
        self.__dest_dir_btn.setFixedWidth(
            1.1 * self.__src_dir_btn.fontMetrics().boundingRect(
                "Select Destination Directory").width())
        self.__dest_dir_btn.setFixedHeight(button_height)
        self.__dest_dir_btn.clicked.connect(self.__show_dest_dir_dialog)
        self.__dest_dir_btn.move(20, 10 + 6.25 * scale_factor * text_height)

        # combo box for available variables
        self.__variable_box_title = QtWidgets.QLabel(self)
        self.__variable_box_title.setFont(font)
        self.__variable_box_title.setText("Variables Available for Extraction")
        self.__variable_box_title.setFixedWidth(
            20 + self.__variable_box_title.fontMetrics().boundingRect(
                "Variables Available for Extraction").width())
        self.__variable_box_title.move(20, 10 + 8 * scale_factor * text_height)
        self.__variable_box = QComboBox(self)
        self.__variable_box.setFont(font)
        self.__variable_box.setFixedWidth(
            self.__variable_box.fontMetrics().boundingRect(15 * "X").width())
        self.__variable_box.move(20, 10 + 9.25 * scale_factor * text_height)
        self.__variable_box.currentIndexChanged.connect(
            self.__update_variable_info)
        self.__variable_box_info = QtWidgets.QLabel(self)
        self.__variable_box_info.setFont(font)
        self.__variable_box_info.setText("Full Variable Name")
        self.__variable_box_info.setFixedWidth(
            20 +
            self.__variable_box_info.fontMetrics().boundingRect(200 *
                                                                "X").width())
        self.__variable_box_info.move(180,
                                      10 + 9.25 * scale_factor * text_height)

        # extract button
        self.__extract_btn = QPushButton("Extract", self)
        self.__extract_btn.setFont(font)
        self.__extract_btn.setFixedWidth(
            20 +
            self.__extract_btn.fontMetrics().boundingRect("Extract").width())
        self.__extract_btn.setFixedHeight(button_height)
        self.__extract_btn.clicked.connect(self.__extract)
        self.__extract_btn.move(20, 10 + 11.25 * scale_factor * text_height)
        self.__extract_btn.setEnabled(False)

        # create the progress bar
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(20, 10 + 13 * scale_factor * text_height,
                                     window_width - 40, button_height)

        # TODO: reactive this
        # exitAct = QAction('&Exit', self)
        # exitAct.setShortcut('Ctrl+Q')
        # exitAct.setStatusTip('Exit Application')
        #        exitAct.triggered.connect(qApp.quit)

        self.statusBar().showMessage('Ready')

        self.setGeometry(300, 300, window_width, window_height)
        self.setWindowTitle("NetCDF File Converter")
        self.__center_window()
        self.show()

    @pyqtSlot(float)
    def __update_extraction_bar(self, progress: float):
        self.progressBar.setValue(progress)

    def __update_variable_info(self):
        if not self.__variable_box.currentText() is None:
            self.__long_variable_name = DataProcessor.get_long_variable_name(
                self.__src_dir_path, self.__variable_box.currentText())
            self.__variable_box_info.setText(self.__long_variable_name)

    def __extract(self):
        self.__extract_btn.setEnabled(False)
        if self.__dest_dir_path == "":
            print("please input a path")
            exit(-1)

        self.thread = DataProcessor(self.__src_dir_path, self.__dest_dir_path,
                                    self.__variable_box.currentText())
        self.thread.extraction_progress_update.connect(
            self.__update_extraction_bar)
        self.thread.finished.connect(self.__re_enable_extract_btn)
        self.thread.extraction_status_message.connect(self.__update_status_bar)
        self.thread.start()

    def __re_enable_extract_btn(self):
        self.__extract_btn.setEnabled(True)

    def __update_status_bar(self, status: str):
        self.statusBar().showMessage(status)

    def __show_dest_dir_dialog(self):
        self.statusBar().showMessage('Ready')
        file_name = QFileDialog.getExistingDirectory(
            self, "Select Destination Directory")

        if file_name:
            self.__dest_dir_label.setText(file_name)
            self.__dest_dir_path = file_name

    def __show_src_dir_dialog(self):
        self.statusBar().showMessage('Ready')
        file_name = QFileDialog.getExistingDirectory(
            self, "Select Source Directory")

        if file_name:
            self.__src_dir_label.setText(file_name)
            self.__src_dir_path = file_name
            self.__variable_box.clear()
            self.__variable_box.addItems(
                DataProcessor.get_available_variables(self.__src_dir_path))
            self.__extract_btn.setEnabled(True)

    def __center_window(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
