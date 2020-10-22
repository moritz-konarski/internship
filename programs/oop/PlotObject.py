from enum import Enum

class PlotType(Enum):
    TimeSeries = auto()
    HeatMap = auto()
    HeatMapSeries = auto()


class PlotObject:

    def __init__(self, type: PlotType, variable: str, data):
        this.type = type
        this.variable = variable
        this.data = data


class TimeSeries(PlotObject):

    def __init__(self, type: PlotType, variable: str, data):
        super(type, variable, data)


class HeatMap(PlotObject):

    def __init__(self, type: PlotType, variable: str, data):
        super(type, variable, data)


class HeatMapSeries(PlotObject):

    def __init__(self, type: PlotType, variable: str, data):
        super(type, variable, data)