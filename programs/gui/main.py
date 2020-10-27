#!/usr/bin/python

import sys
import warnings
warnings.filterwarnings("ignore")
from GUI import GUI
from PyQt5.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    gui = GUI()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
