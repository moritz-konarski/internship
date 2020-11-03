from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from DataProcessorTab import DataProcessorTab


class Tabs(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        self.parent = parent
        self.margin = 20
        self.element_height = 25
        self.button_width = 200

        self.tabs = QTabWidget()

        self.tab1 = DataProcessorTab(self)
        self.tabs.addTab(self.tab1, self.tab1.title)

        self.tab2 = QWidget()
        self.tabs.addTab(self.tab2, "For")

        self.tab3 = QWidget()
        self.tabs.addTab(self.tab3, "Geeks")

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
