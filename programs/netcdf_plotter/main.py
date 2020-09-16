#!/usr/bin/env python

# This is a sample Python script.
# https://disc.gsfc.nasa.gov/information/howto?title=How%20to%20read%20and%20plot%20NetCDF%20MERRA-2%20data%20in%20Python

# plotting stuff
# https://scitools.org.uk/cartopy/docs/v0.15/matplotlib/advanced_plotting.html

# cartopy
# https://scitools.org.uk/cartopy/docs/latest/crs/projections.html

from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
# TODO: set up cli app
# import fire

import warnings

# TODO: try to fix these warnings
# this is needed because netcdf4 emits warnings that I cannot fix when printing
# data
warnings.filterwarnings("ignore", category=DeprecationWarning)
# errors from mismatched libraries
warnings.filterwarnings("ignore", category=RuntimeWarning)

# TODO: make all of this modular

my_example_nc_file = '../.downloads_2/20200701.nc4'
file_format = 'png'
file_dpi = 500


def read_var_info() -> {str: (str, str)}:
    with Dataset(my_example_nc_file, mode='r') as data:
        data_dict = dict()
        for var in data.variables.keys():
            data_dict[var] = (
                data.variables[var].long_name,
                data.variables[var].dimensions)
    return data_dict


# this as one option for the cli app -- list to see this
# TODO: add unit to this
def print_var_info(data_dict: {str: (str, str)}):
    for key in data_dict.keys():
        print(key)
        print("  long name:  " + data_dict[key][0])
        print("  dimensions: " + str(data_dict[key][1]))


def list():
    print_var_info(read_var_info())


# TODO: read lon, lat info from file and plot accordingly
#


def create_graph(var: str, name: str):
    with Dataset(my_example_nc_file, mode='r') as data:
        lons: [float] = data.variables['lon'][:]
        lats: [float] = data.variables['lat'][:]

        min, max = find_range(var)

        d = data.variables[var][:, :, :]
        d: [float, float, float] = d[0, :, :]

        # Set the figure size, projection, and extent
        fig = plt.figure(figsize=(10, 6))

        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.set_global()
        ax.set_extent([65, 83, 34, 48], crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.BORDERS, linewidth=1.4)
        ax.gridlines(linestyle='--', color='black', draw_labels=True,
                     linewidth=0.5)

        res = int((max - min) / 20)

        # Set contour levels, then draw the plot and a colorbar
        clevs = np.arange(min, max, res)
        plt.contourf(lons, lats, d, clevs, transform=ccrs.PlateCarree(),
                     cmap=plt.cm.jet)

        cb = plt.colorbar(ax=ax, orientation="vertical", pad=0.02, aspect=16,
                          shrink=0.8)

        cb.ax.tick_params(labelsize=10)
        # TODO: make this more intelligent -- get time and date from file
        if name == 'ps':
            plt.title('Surface Pressure at 12am 01.07.2020', size=14)
            cb.set_label('Pa', size=12, rotation=0, labelpad=15)
        elif name == 'phis':
            plt.title('Surface Geopotential Height at 12am 01.07.2020', size=14)
            cb.set_label('m^2/s^-2', size=12, rotation=0, labelpad=15)

        # Save the plot as a PNG image
        fig.savefig('nc_plot_' + name + '.png', format=file_format,
                    dpi=file_dpi)


def list_all_var_data():
    with Dataset(my_example_nc_file, mode='r') as data:
        print(data.variables)


def find_range(var_name):
    with Dataset(my_example_nc_file, mode='r') as data:
        var = data.variables[var_name]
        max = var[:].max()
        min = var[:].min()
    return min, max


# TODO: use numpy variables for speed and accuracy -- read the type from input
#  , save in dict

if __name__ == '__main__':
    with Dataset(my_example_nc_file, mode='r') as cdata:
        # list()
        # list_all_var_data()
        # print(find_range('PS'))
        create_graph('PS', 'ps')
        create_graph('PHIS', 'phis')
