import os
import webbrowser

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QMenuBar, QAction

from DataExporterTab import DataExporterTab
from DataManagerTab import DataManagerTab, DataAction
from DataPlotterTab import DataPlotterTab
from DataProcessorTab import DataProcessorTab


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

        self.menubar = QMenuBar(self)
        self.help_menu = self.menubar.addMenu('&Help')
        help_action = QAction('&Help', self)
        help_action.triggered.connect(self.show_help)
        self.help_menu.addAction(help_action)

        # add the tabs to the window
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.menubar)
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

    def show_help(self):
        webbrowser.open(os.path.abspath(os.path.join(os.path.dirname(__file__), "./help/index.html")))