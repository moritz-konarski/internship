import sys
from PyQt5.QtWidgets import (QWidget, QToolTip, QPushButton, QApplication,
                             QMessageBox, QDesktopWidget, QMainWindow, QAction,
                             qApp, QMenu)
from PyQt5.QtGui import QFont
from PyQt5.uic.properties import QtGui


class GUI(QMainWindow):

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        QToolTip.setFont(QFont('SansSerif', 10))

        self.setToolTip('This is a <b>QWidget</b> widget')

        btn = QPushButton('Button', self)
        btn.setToolTip('This is a <b>QPushButton</b> widget')
        btn.resize(btn.sizeHint())
        btn.move(50, 50)

        qbtn = QPushButton('Quit', self)
        qbtn.setToolTip('This is a <b>Quit</b> button')
        qbtn.resize(qbtn.sizeHint())
        qbtn.clicked.connect(QApplication.instance().quit)
        qbtn.move(150, 50)

        # what does this do
        exitAct = QAction('&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit Application')
        # this can be any function -- this is how I can do it
        exitAct.triggered.connect(qApp.quit)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)

        impMenu = QMenu('Import', self)
        impAct = QAction('Import mail', self)
        impMenu.addAction(impAct)

        newAct = QAction('New', self)

        fileMenu.addAction(newAct)
        fileMenu.addMenu(impMenu)

        self.statusBar().showMessage('Ready')

        self.setGeometry(300, 300, 800, 500)
        self.setWindowTitle("NetCDF File Converter")
        self._center_window()
        self.show()

    # override of the standard event
    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Message",
                                     "Are you sure you want to quit?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def contextMenuEvent(self, event):
        cmenu = QMenu(self)

        newAct = cmenu.addAction("New")
        openAct = cmenu.addAction("Open")
        quitAct = cmenu.addAction("Quit")
        action = cmenu.exec_(self.mapToGlobal(event.pos()))

        if action == quitAct:
            qApp.quit()

    def _center_window(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def test(self):
        print("testing")