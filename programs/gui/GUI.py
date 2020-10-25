import sys
from DataProcessor import DataProcessor
from pathlib import Path

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QWidget, QToolTip, QPushButton, QApplication,
                             QMessageBox, QDesktopWidget, QMainWindow, QAction,
                             qApp, QMenu, QPushButton, QFileDialog, QLineEdit,
                             QComboBox)
from PyQt5.QtGui import QFont
from PyQt5.uic.properties import QtGui


class GUI(QMainWindow):

    def __init__(self):
        super().__init__()
        self.__init_ui()
        self.__src_dir_path = ""
        self.__dest_dir_path = ""
        self.__var_name_list = []
        self.__data_processor = None

    def __init_ui(self):
        scale_factor = 1.3
        font = self.font()
        font.setPointSize(11)
        window_height = 500
        window_width = 600
        # source directory label and message box
        self.__src_dir_title = QtWidgets.QLabel(self)
        self.__src_dir_title.setFont(font)
        text_height = self.__src_dir_title.fontMetrics().boundingRect(
            "0").height()
        button_height = 1.8 * text_height
        self.__src_dir_title.setText("Source Directory Path")
        self.__src_dir_title.setFixedWidth(
            self.__src_dir_title.fontMetrics().boundingRect(
                255 * "0").width())
        self.__src_dir_title.move(20, 10)
        self.__src_dir_label = QtWidgets.QLabel(self)
        self.__src_dir_label.setFont(font)
        self.__src_dir_label.setText("--")
        self.__src_dir_label.setFixedWidth(
            self.__src_dir_label.fontMetrics().boundingRect(
                255 * "0").width())
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
            self.__src_dir_title.fontMetrics().boundingRect(
                255 * "0").width())
        self.__dest_dir_title.move(20, 10 + 4 * scale_factor * text_height)
        self.__dest_dir_label = QtWidgets.QLabel(self)
        self.__dest_dir_label.setFont(font)
        self.__dest_dir_label.setText("--")
        self.__dest_dir_label.setFixedWidth(
            self.__src_dir_label.fontMetrics().boundingRect(
                255 * "0").width())
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
        # self.__variable_box.addItem("")
        self.__variable_box.setFont(font)
        self.__variable_box.setFixedWidth(
            self.__variable_box.fontMetrics().boundingRect(15 * "X").width())
        self.__variable_box.move(20, 10 + 9.25 * scale_factor * text_height)

        # extract button
        self.__extract_btn = QPushButton("Extract", self)
        self.__extract_btn.setFont(font)
        self.__extract_btn.setFixedWidth(
            20 + self.__extract_btn.fontMetrics().boundingRect(
                "Extract").width())
        self.__extract_btn.setFixedHeight(button_height)
        self.__extract_btn.clicked.connect(self.__extract)
        self.__extract_btn.move(20, 10 + 11.25 * scale_factor * text_height)

        # drop-down list of all the available variables
        # becomes a thing when src_dir is selected

        # self.setToolTip('This is a <b>QWidget</b> widget')

        # openFile = QAction("Open", self)
        # openFile.setShortcut("Ctrl+O")
        # openFile.setStatusTip("Open New File")
        # openFile.triggered.connect(self.show_src_dir_dialog)

        # dest_file_label = QtWidgets.QLabel(self)
        # dest_file_label.setText("Dest Path")
        # dest_file_label.move(250, 150)

        # self.le = QLineEdit(self)
        # self.le.move(130, 22)

        # btn = QPushButton('Button', self)
        # btn.setToolTip('This is a <b>QPushButton</b> widget')
        # btn.resize(btn.sizeHint())
        # btn.move(50, 50)

        # qbtn = QPushButton('Quit', self)
        # qbtn.setToolTip('This is a <b>Quit</b> button')
        # qbtn.resize(qbtn.sizeHint())
        # qbtn.clicked.connect(QApplication.instance().quit)
        # qbtn.move(150, 50)

        # TODO: reactive this
        # exitAct = QAction('&Exit', self)
        # exitAct.setShortcut('Ctrl+Q')
        # exitAct.setStatusTip('Exit Application')
        #        exitAct.triggered.connect(qApp.quit)

        # menubar = self.menuBar()
        # fileMenu = menubar.addMenu('&File')
        # fileMenu.addAction(exitAct)

        # impMenu = QMenu('Import', self)
        # impAct = QAction('Import mail', self)
        # impMenu.addAction(impAct)

        # newAct = QAction('New', self)

        # fileMenu.addAction(newAct)
        # fileMenu.addMenu(impMenu)

        self.statusBar().showMessage('Ready')

        self.setGeometry(300, 300, window_width, window_height)
        self.setWindowTitle("NetCDF File Converter")
        self.__center_window()
        self.show()

    def __show_src_dir_dialog(self):
        self.statusBar().showMessage('Ready')
        file_name = QFileDialog.getExistingDirectory(self,
                                                     "Select Source Directory")

        if file_name:
            self.__src_dir_label.setText(file_name)
            self.__src_dir_path = file_name
            if self.__dest_dir_path != "":
                self.__create_data_processor()

    def __extract(self):
        self.statusBar().showMessage(
            "Extracting " + self.__variable_box.currentText() + "...")
        self.__data_processor.extract_variable(self.__variable_box.currentText()
                                               )
        self.statusBar().showMessage("Extraction Complete")

    def __show_dest_dir_dialog(self):
        self.statusBar().showMessage('Ready')
        file_name = QFileDialog.getExistingDirectory(self,
                                                     "Select Destination Directory")

        if file_name:
            self.__dest_dir_label.setText(file_name)
            self.__dest_dir_path = file_name
            if self.__src_dir_path != "":
                self.__create_data_processor()

    def __create_data_processor(self):
        self.statusBar().showMessage('Ready')
        self.__data_processor = DataProcessor(self.__src_dir_path,
                                              self.__dest_dir_path)
        self.__var_name_list = self.__data_processor.get_available_variables()
        self.__variable_box.addItems(self.__var_name_list)

    # override of the standard event
    # def closeEvent(self, event):
    #    reply = QMessageBox.question(self, "Message",
    #                                 "Are you sure you want to quit?",
    #                                 QMessageBox.Yes | QMessageBox.No,
    #                                 QMessageBox.No)

    #    if reply == QMessageBox.Yes:
    #        event.accept()
    #    else:
    #        event.ignore()

    # def contextMenuEvent(self, event):
    #    cmenu = QMenu(self)

    #    newAct = cmenu.addAction("New")
    #    openAct = cmenu.addAction("Open")
    #    quitAct = cmenu.addAction("Quit")
    #    action = cmenu.exec_(self.mapToGlobal(event.pos()))

    #    if action == quitAct:
    #        qApp.quit()

    def __center_window(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
