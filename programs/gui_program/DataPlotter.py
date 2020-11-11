from textwrap import wrap

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal

from DataManager import DataManager
from DataObject import DataObject
from HelperFunctions import PlotDataType, PlotType, HelperFunction as hf

# city   longitude, latitude, name
bishkek = (74.5698, 42.8746, "Bishkek")
almaty = (76.8512, 43.2220, "Almaty")
kabul = (69.2075, 34.5553, "Kabul")
tashkent = (69.2401, 41.2995, "Tashkent")
dushanbe = (68.7870, 38.5598, "Dushanbe")


class DataPlotter(QThread):
    is_plotting = pyqtSignal(bool)
    finished = pyqtSignal()

    def __init__(self, data_manager: DataManager):
        super().__init__()
        self.path = None
        self.file_name = None
        self.plot_file_type = None
        self.data_manager = data_manager
        self.is_running = False

        self.figure_width = 9.5
        self.figure_height = 6
        self.file_dpi = 300
        self.is_background_transparent = False
        self.inch_padding = 0.1

        self.plot_cities = True
        self.use_local_min_max = False

    def set_attributes(self, data_type: str, path: str):
        self.plot_file_type = data_type
        self.path = path

    def set_plot_cities(self, enabled: bool):
        self.plot_cities = enabled

    def set_use_local_min_max(self, enabled: bool):
        self.use_local_min_max = enabled

    def update_attributes(self, data_object: DataObject):
        if not self.is_running:
            return
        if data_object.plot_type == PlotType.TIME_SERIES:
            if len(self.data_manager.shape) == 4:
                self.file_name = "Time Series " + data_object.long_name + " " + hf.get_str_from_datetime(
                    data_object.start_time) + "-" + hf.get_str_from_datetime(
                    data_object.end_time) + " (" + str(
                    data_object.lat_min) + "N, " + str(
                    data_object.lon_min) + "E) " + str(
                    hf.round_number(data_object.level,
                                    2)) + " hPa"
            else:
                self.file_name = "Time Series " + data_object.long_name + " " + hf.get_str_from_datetime(
                    data_object.start_time) + "-" + hf.get_str_from_datetime(
                    data_object.end_time) + " (" + str(
                    data_object.lat_min) + "N, " + str(
                    data_object.lon_min) + "E)"
        elif data_object.plot_type == PlotType.HEAT_MAP:
            if len(self.data_manager.shape) == 4:
                self.file_name = "Heat Map " + data_object.long_name + " " + hf.get_str_from_datetime(
                    data_object.start_time) + " (" + str(
                    data_object.lat_min) + "N, " + str(
                    data_object.lon_min) + "E)-(" + str(
                    data_object.lat_max) + "N, " + str(
                    data_object.lon_max) + "E) " + str(
                    hf.round_number(data_object.level,
                                    2)) + " hPa"
            else:
                self.file_name = "Heat Map " + data_object.long_name + " " + hf.get_str_from_datetime(
                    data_object.start_time) + " (" + str(
                    data_object.lat_min) + "N, " + str(
                    data_object.lon_min) + "E)-(" + str(
                    data_object.lat_max) + "N, " + str(
                    data_object.lon_max) + "E)"

    def plot_files(self):
        self.is_plotting.emit(True)
        figure = None
        for data_object in iter(self.data_manager):
            if not self.is_running:
                self.is_plotting.emit(False)
                return
            self.update_attributes(data_object)
            if not self.is_running:
                self.is_plotting.emit(False)
                return
            if data_object.plot_type == PlotType.TIME_SERIES:
                if not self.is_running:
                    self.is_plotting.emit(False)
                    return
                figure = self.plot_time_series(data_object)
            elif data_object.plot_type == PlotType.HEAT_MAP:
                if not self.is_running:
                    self.is_plotting.emit(False)
                    return
                figure = self.plot_heat_map(data_object)
                pass

            if not self.is_running:
                self.is_plotting.emit(False)
                return
            if self.plot_file_type == PlotDataType.EPS.value:
                with open(
                        self.path + self.file_name + '.' +
                        PlotDataType.EPS.value, 'wb') as f:
                    figure.savefig(f,
                                   format=PlotDataType.EPS.value,
                                   dpi=self.file_dpi,
                                   transparent=self.is_background_transparent,
                                   bbox_inches='tight',
                                   pad_inches=self.inch_padding)
            elif self.plot_file_type == PlotDataType.PDF.value:
                with open(
                        self.path + self.file_name + '.' +
                        PlotDataType.PDF.value, 'wb') as f:
                    figure.savefig(f,
                                   format=PlotDataType.PDF.value,
                                   dpi=self.file_dpi,
                                   transparent=self.is_background_transparent,
                                   bbox_inches='tight',
                                   pad_inches=self.inch_padding)
            elif self.plot_file_type == PlotDataType.PNG.value:
                with open(
                        self.path + self.file_name + '.' +
                        PlotDataType.PNG.value, 'wb') as f:
                    figure.savefig(f,
                                   format=PlotDataType.PNG.value,
                                   dpi=self.file_dpi,
                                   transparent=self.is_background_transparent,
                                   bbox_inches='tight',
                                   pad_inches=self.inch_padding)
            elif self.plot_file_type == PlotDataType.SVG.value:
                with open(
                        self.path + self.file_name + '.' +
                        PlotDataType.SVG.value, 'wb') as f:
                    figure.savefig(f,
                                   format=PlotDataType.SVG.value,
                                   dpi=self.file_dpi,
                                   transparent=self.is_background_transparent,
                                   bbox_inches='tight',
                                   pad_inches=self.inch_padding)
            elif self.plot_file_type == PlotDataType.JPEG.value:
                with open(
                        self.path + self.file_name + '.' +
                        PlotDataType.JPEG.value, 'wb') as f:
                    figure.savefig(f,
                                   format=PlotDataType.JPEG.value,
                                   dpi=self.file_dpi,
                                   transparent=self.is_background_transparent,
                                   bbox_inches='tight',
                                   pad_inches=self.inch_padding)
        self.is_plotting.emit(False)
        self.finished.emit()

    def plot_heat_map(self, data_object: DataObject):

        lats = data_object.lats
        lons = data_object.lons

        fig = plt.figure(figsize=(self.figure_width, self.figure_height))

        emin = data_object.lon_min
        emax = data_object.lon_max
        nmin = data_object.lat_min
        nmax = data_object.lat_max

        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.set_global()
        ax.set_extent([emin, emax, nmin, nmax], crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.BORDERS, linewidth=1.4)
        ax.gridlines(linestyle='--',
                     color='black',
                     draw_labels=True,
                     linewidth=0.5)

        if self.use_local_min_max:
            res = float(
                (data_object.object_data_max - data_object.object_data_min) /
                50)

            clevs = np.arange(data_object.object_data_min,
                              data_object.object_data_max + res,
                              res,
                              dtype=float)
            plt.contourf(lons,
                         lats,
                         data_object.data,
                         clevs,
                         transform=ccrs.PlateCarree(),
                         cmap=plt.cm.jet)
        else:
            res = float((data_object.data_max - data_object.data_min) / 50)

            clevs = np.arange(data_object.data_min,
                              data_object.data_max + res,
                              res,
                              dtype=float)
            plt.contourf(lons,
                         lats,
                         data_object.data,
                         clevs,
                         transform=ccrs.PlateCarree(),
                         cmap=plt.cm.jet)

        cb = plt.colorbar(ax=ax,
                          orientation="vertical",
                          pad=0.08,
                          aspect=16,
                          shrink=0.8)

        cb.ax.tick_params(labelsize=10, pad=0.5)

        if self.plot_cities:
            plt.plot(bishkek[0],
                     bishkek[1],
                     color='black',
                     markersize=3,
                     marker='o',
                     transform=ccrs.PlateCarree())

            ax.text(bishkek[0],
                    bishkek[1] - 0.5,
                    bishkek[2],
                    horizontalalignment='center',
                    transform=ccrs.PlateCarree())

            plt.plot(almaty[0],
                     almaty[1],
                     color='black',
                     markersize=3,
                     marker='o',
                     transform=ccrs.PlateCarree())

            ax.text(almaty[0],
                    almaty[1] + 0.25,
                    almaty[2],
                    horizontalalignment='center',
                    transform=ccrs.PlateCarree())

            plt.plot(kabul[0],
                     kabul[1],
                     color='black',
                     markersize=3,
                     marker='o',
                     transform=ccrs.PlateCarree())

            ax.text(kabul[0],
                    kabul[1] + 0.25,
                    kabul[2],
                    horizontalalignment='center',
                    transform=ccrs.PlateCarree())

            plt.plot(tashkent[0],
                     tashkent[1],
                     color='black',
                     markersize=3,
                     marker='o',
                     transform=ccrs.PlateCarree())

            ax.text(tashkent[0] - 0.9,
                    tashkent[1] + 0.25,
                    tashkent[2],
                    horizontalalignment='center',
                    transform=ccrs.PlateCarree())

            plt.plot(dushanbe[0],
                     dushanbe[1],
                     color='black',
                     markersize=3,
                     marker='o',
                     transform=ccrs.PlateCarree())

            ax.text(dushanbe[0] + 0.65,
                    dushanbe[1] + 0.25,
                    dushanbe[2],
                    horizontalalignment='center',
                    transform=ccrs.PlateCarree())

        plt.title("\n".join(wrap(self.file_name, 60)),
                  size=18,
                  loc='left',
                  pad=20,
                  wrap=True)

        cb.set_label(data_object.unit, size=12, rotation=90, labelpad=10)

        return fig

    def plot_time_series(self, data_object: DataObject):
        plt.style.use('seaborn-whitegrid')

        fig = plt.figure(figsize=(self.figure_width, self.figure_height))

        ax = plt.axes()

        ax.plot(data_object.data)
        plt.gcf().autofmt_xdate()

        plt.title("\n".join(wrap(self.file_name, 60)),
                  size=18,
                  loc='left',
                  pad=20,
                  wrap=True)

        plt.ylabel(data_object.unit)
        if self.use_local_min_max:
            plt.ylim(data_object.object_data_min, data_object.object_data_max)
        else:
            plt.ylim(data_object.data_min, data_object.data_max)
        plt.xlabel("Time")
        return fig

    @pyqtSlot()
    def run(self):
        self.is_running = True
        self.plot_files()

    def stop(self):
        self.is_running = False
