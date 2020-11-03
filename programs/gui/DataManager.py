from PlotObject import PlotType
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal


class DataManager(QThread):
    def __init__(self, path: str):
        self.thread_running = False
        # here we initialize the data manager
        self.metadata = ['die', 'there']
        pass

    @pyqtSlot()
    def run(self):
        self.thread_running = True
        pass

    def stop(self):
        self.thread_running = False
        pass

    @property
    def metadata(self):
        return self.metadata

    def get_plot_data(self, plot_type: PlotType):
        # return the appropriate type of slice
        pass
