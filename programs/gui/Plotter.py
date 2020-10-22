from PlotObject import PlotObject


class Plotter:

    def __init__(self):
        pass

    def plot(self, plot_object: PlotObject = None):
        if plot_object is None:
            print("please add plot_object")
        else:
            print("cool")
