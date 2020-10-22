from PlotObject import PlotType


class DataManager:

    def __init__(self, path: str):
        # here we initialize the data manager
        self.metadata = ['die', 'there']
        pass

    @property
    def metadata(self):
        return self.metadata

    def get_plot_data(self, plot_type: PlotType):
        # return the appropriate type of slice
        pass
