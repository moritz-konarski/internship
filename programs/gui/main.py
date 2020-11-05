#!/usr/bin/python

import sys
import warnings

from PyQt5.QtWidgets import QApplication

from GUI import GUI

warnings.filterwarnings("ignore")


# TODO: fix all the naming

def main():
    app = QApplication(sys.argv)
    gui = GUI()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
