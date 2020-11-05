from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from DataProcessorTab import DataProcessorTab
from DataManagerTab import DataManagerTab


class Tabs(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.margin = 20
        self.element_height = 25
        self.button_width = 200

        self.tabs = QTabWidget()

        self.tab1 = DataProcessorTab(self)
        self.tabs.addTab(self.tab1, self.tab1.title)

        self.tab2 = DataManagerTab(self)
        self.tab2.is_data_selected.connect(self.set_subtabs_enabled)
        self.tabs.addTab(self.tab2, self.tab2.title)

        self.sub_tabs = QTabWidget()
        self.sub_tab1 = QWidget()
        self.sub_tab2 = QWidget()
        self.sub_tabs.addTab(self.sub_tab1, "Heat Map")
        self.sub_tabs.addTab(self.sub_tab2, "Time Series")

        self.sub_tabs.setDisabled(True)

        self.tab3 = QWidget()
        self.tabs.addTab(self.sub_tabs, "Plot Data")

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def set_subtabs_enabled(self, enabled: bool):
        self.sub_tabs.setEnabled(enabled)
