from textwrap import wrap

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from DataExporterTab import DataExporterTab
from DataManagerTab import DataManagerTab, DataAction
from DataPlotterTab import DataPlotterTab
from DataProcessorTab import DataProcessorTab
from HelperFunctions import HelperFunction as hf


class TabWidget(QWidget):
    horizontal_margin = 20
    element_height = 25
    button_width = 200

    def __init__(self, main_gui):
        super().__init__()

        self.main_gui = main_gui

        # main tab widget
        self.tabs = QTabWidget()

        # data processing tab, first tab
        self.tab1 = DataProcessorTab(self)
        self.tabs.addTab(self.tab1, self.tab1.title)

        # data manager tab, second tab
        self.tab2 = DataManagerTab(self)
        self.tabs.addTab(self.tab2, self.tab2.title)
        # enable / disable plotting and export tabs if the appropriate data has been submitted
        self.tab2.data_selection_signal.connect(self.enable_tabs)

        # data export tab, 3rd tab
        self.tab3 = DataExporterTab(self)
        # disable this tab by default because user input is needed to validate it
        self.tabs.addTab(self.tab3, self.tab3.title)
        self.tab3.setEnabled(False)

        # plotting tab, 4th tab
        self.tab4 = DataPlotterTab(self)
        self.tabs.addTab(self.tab4, self.tab4.title)
        # disable this tab by default because user input is needed to validate it
        self.tab4.setEnabled(False)

        self.tab5 = QTabWidget(self)

        self.sub_tab1 = QWidget(self)
        font = self.sub_tab1.font()
        font.setPointSize(11)
        self.sub_tab1.setFont(font)
        self.sub_tab1.label = hf.create_label(self.sub_tab1, "\n".join(
            wrap(data_processor_help_text, 90)), 20, 20,
                                              0.7 * self.main_gui.height)
        self.tab5.addTab(self.sub_tab1, "Data Processor")

        self.sub_tab2 = QWidget(self)
        font = self.sub_tab2.font()
        font.setPointSize(11)
        self.sub_tab2.setFont(font)
        self.sub_tab2.label = hf.create_label(self.sub_tab2, "\n".join(
            wrap(data_manager_help_text, 90)), 20, 20,
                                              0.7 * self.main_gui.height)
        self.tab5.addTab(self.sub_tab2, "Data Manager")

        self.sub_tab3 = QWidget(self)
        font = self.sub_tab3.font()
        font.setPointSize(11)
        self.sub_tab3.setFont(font)
        self.sub_tab3.label = hf.create_label(self.sub_tab3, "\n".join(
            wrap(data_exporter_help_text, 90)), 20, 20,
                                              0.7 * self.main_gui.height)
        self.tab5.addTab(self.sub_tab3, "Export Data")

        self.sub_tab4 = QWidget(self)
        font = self.sub_tab4.font()
        font.setPointSize(11)
        self.sub_tab4.setFont(font)
        self.sub_tab4.label = hf.create_label(self.sub_tab4, "\n".join(
            wrap(data_plotter_help_text, 87)), 20, 20,
                                              0.7 * self.main_gui.height)
        self.tab5.addTab(self.sub_tab4, "Plot Data")

        self.tabs.addTab(self.tab5, "Help")

        # add the tabs to the window
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def enable_tabs(self, enabled: bool, action: DataAction):
        if action == DataAction.EXPORT:
            self.tab3.setEnabled(enabled)
            self.tab4.setDisabled(enabled)
            self.tabs.setCurrentIndex(2)
            self.tab3.set_data_manager(self.tab2.get_data_manager())
        elif action == DataAction.PLOT:
            self.tab4.setEnabled(enabled)
            self.tab3.setDisabled(enabled)
            self.tabs.setCurrentIndex(3)
            self.tab4.set_data_manager(self.tab2.get_data_manager())


data_processor_help_text = "The Data Processor is responsible for converting NetCDF files into NPZ files. It extracts the specified variable and metadata.\nTo select a source directory, press the \"Select Source Directory\" button. The source directory must contain NetCDF files (*.nc4).\n To select a variable to extract, select it from the combo box. The full name of the variable will be displayed for convenience.\nTo begin the extraction and choose a destination directory, press the \"Extract\" button. Press \"Cancel Extraction\" to stop the extraction before it is complete. The data will be saved in a new folder in the destination directory that is named the same as the variable. Attention: if the source directory contains many NetCDF files, the extraction process might take multiple minutes."

data_manager_help_text = "The Data Manager is responsible for selecting a subset of the data extracted using the Data Processor. It is also responsible for selecting the type of data that should be used. The available options are time series and heat map. To select a source directory (the one created by the Data Processor) press the \"Select Source Directory\" button. Next, select which type of data you want to use. Then use the table to enter the minimum and maximum values you want your data to have. Here the minimum and maximum values that the data contains are shown and all input is validated. The table automatically adjusts to the type of data requested. Finally, click on either the \"Export Data\" or the \"Plot Data\" button to start the associated processes. Take note that you may always come back to this tab and change some of the values because they are saved while the data export or data plotting happens."

data_exporter_help_text = "Exporting Data is the process of saving the data extracted using the Data Processor in a different format. This might be desirable in case one would like to perform some analysis this program does not support or wishes to share this data in a more common format. To export data, simply select the file type you want to export to and click \"Export\". The data selected in the data manager will be exported to the selelcted file type. It will be saved in a folder called \"<variable nane>-exported\" which will be created in the folder you select after clicking \"Export\". If you chose heat map data, for each time step in your time selection one file containing the corresponding information will be saved. If your data has pressure levels, each of them will be saved in a separate file. For time series data each pressure level is saved to separate file. This can quickly lead to large numbers of files and thus a popup window will inform you how many files will be created so the parameters can be adjusted if needed."

data_plotter_help_text = "The Data Plotter creates graphs based on the in the Data Manager selected data. The user may choose which file type the graphs should be saved as. Then a choice has to be made whether to use global or local minimum and maximum values. Using global min and max values means that all graphs will have the same scale while local min and max are unique to each file. For heat map data there is an additional option to add the larger cities of the region to the graph. If time series data was selected, each pressure level (if applicable) will be graphed separately. If heat map data was selected, for each time step and for each pressure level per time step (if applicable) a graph will be generated. Because this can lead to large numbers of files, a popup will warn the user how many files would be created. The files will be saved in a directory called \"<variable name>-plotted\" in the destination directory the user chooses after clicking \"Plot\"."
