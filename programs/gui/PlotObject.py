from enum import Enum, auto


class PlotType(Enum):
    TimeSeries = auto()
    HeatMap = auto()
    HeatMapSeries = auto()


class PlotObject:

    def __init__(self, plot_type: PlotType, variable: str, data):
        self.type = plot_type
        self.variable = variable
        self.data = data


class TimeSeries(PlotObject):

    def __init__(self, plot_type: PlotType = None, variable: str = None,
                 data=None):
        super().__init__(plot_type, variable, data)


class HeatMap(PlotObject):

    def __init__(self, plot_type: PlotType, variable: str, data):
        super().__init__(plot_type, variable, data)


class HeatMapSeries(PlotObject):

    def __init__(self, plot_type: PlotType, variable: str, data):
        super().__init__(plot_type, variable, data)
