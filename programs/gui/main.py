#!/usr/bin/python

import sys
import warnings
from GUI import GUI
from PyQt5.QtWidgets import QApplication

warnings.filterwarnings("ignore")


def main():
    app = QApplication(sys.argv)
    gui = GUI()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
