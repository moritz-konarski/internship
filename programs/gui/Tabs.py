from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from DataManagerTab import DataManagerTab, DataAction
from DataProcessorTab import DataProcessorTab
from ExportDataTab import ExportDataTab


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

        # TODO: add an overlay that explains why it's deactivated
        # data export tab, 3rd tab
        self.tab3 = ExportDataTab(self)
        # disable this tab by default because user input is needed to validate it
        self.tabs.addTab(self.tab3, self.tab3.title)
        self.tab3.setEnabled(False)

        # TODO: add an overlay that explains why it's deactivated, make modular dependent on plot type
        # plotting tab, 4th tab
        self.tab4 = QWidget()
        self.tabs.addTab(self.tab4, "Plot Data")
        # disable this tab by default because user input is needed to validate it
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
        if action == DataAction.EXPORT:
            self.tab3.setEnabled(enabled)
            self.tabs.setCurrentIndex(2)
            self.tab3.set_data_manager(self.tab2.get_data_manager())
        elif action == DataAction.PLOT:
            self.tab4.setEnabled(enabled)
            self.tabs.setCurrentIndex(3)
