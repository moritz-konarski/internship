from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from DataManagerTab import DataManagerTab, DataAction
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

        # TODO: add an overlay that explains why it's deactivated, make modular dependent on plot type
        # plotting tab, third tab
        self.tab3 = QWidget()
        self.tabs.addTab(QWidget(), "Plot Data")
        # disable this tab by default because user input is needed to validate it
        self.tab3.setEnabled(False)

        # TODO: add an overlay that explains why it's deactivated
        # data export tab, fourth tab
        self.tab4 = QWidget()
        # disable this tab by default because user input is needed to validate it
        self.tabs.addTab(self.tab4, "Export Data")
        self.tab4.setEnabled(False)

        # TODO: flesh out the help section
        #   - give this widget tabs that correspond to the individual main tabs
        self.tab5 = QWidget()
        self.tabs.addTab(self.tab5, "Help")

        # add the tabs to the window
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def enable_tabs(self, enabled: bool, action: DataAction):
        if action == DataAction.PLOT:
            self.tab3.setEnabled(enabled)
        elif action == DataAction.EXPORT:
            self.tab4.setEnabled(enabled)
