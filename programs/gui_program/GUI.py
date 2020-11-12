from PyQt5.QtWidgets import QDesktopWidget, QMainWindow

from Tabs import TabWidget

window_title_long = 'Satellite Data Modification and Plotting Program'
window_title = 'SDMAPP'


class GUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.tab_widget = None
        self.title = window_title_long
        self.width = 750
        self.height = 540

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setFixedSize(self.width, self.height)
        self.center_window()

        self.tab_widget = TabWidget(self)
        self.setCentralWidget(self.tab_widget)

        self.show()

    def center_window(self):
        frame_geometry = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
