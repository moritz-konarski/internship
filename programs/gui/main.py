#!/usr/bin/python

import sys
import warnings

from PyQt5.QtWidgets import QApplication

from GUI import GUI

warnings.filterwarnings("ignore")


# TODO: fix all the naming
# TODO: add tool tips to the most important elements
# TODO: see if creating template classes for main tabs and help tabs would be useful
# TODO: see if a static method that returns the desired elements would cut down the code

def main():
    app = QApplication(sys.argv)
    gui = GUI()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
