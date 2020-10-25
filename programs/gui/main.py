#!/usr/bin/python

from Plotter import Plotter
import DataManager
from PlotObject import TimeSeries
from GUI import GUI
from DataProcessor import DataProcessor
import sys
from PyQt5.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    gui = GUI()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

    #dp = DataProcessor(source_dir="../.month/", destination_dir="./test/")
    #print(dp.get_available_variables())
    #print(dp.get_variable_information())
    #dp.extract_variable(variable_name='EPV')
