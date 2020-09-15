#!/usr/bin/env python
# This is a sample Python script.
# inspired by https://joehamman.com/2013/10/12/plotting-netCDF-data-with-Python/
# https://www2.atmos.umd.edu/~cmartin/python/examples/netcdf_example1.html

from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
#import fire

# this is needed because netcdf4 emits warnings that I cannot fix when printing
# data
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

my_example_nc_file = '../.downloads/20200701.nc4'
destination_file = 'nc_plot.png'
file_format = 'png'
file_dpi = 400


def read_var_info() -> {str: (str, str)}:
    with Dataset(my_example_nc_file, mode='r') as data:
        data_dict = dict()
        for var in data.variables.keys():
            data_dict[var] = (
                data.variables[var].long_name,
                data.variables[var].dimensions)
    return data_dict


# this as one option for the cli app -- list to see this
def print_var_info(data_dict: {str: (str, str)}):
    for key in data_dict.keys():
        print(key)
        print("  long name:  " + data_dict[key][0])
        print("  dimensions: " + str(data_dict[key][1]))


def list():
    print_var_info(read_var_info())


def create_graph(var: str):
    with Dataset(my_example_nc_file, mode='r') as data:
        lons: [float] = data.variables['lon'][:]
        lats: [float] = data.variables['lat'][:]

        d = data.variables[var][:, :, :]
        d: [float, float, float] = d[0, :, :]

        # Set the figure size, projection, and extent
        fig = plt.figure(figsize=(10, 6))
        ax = plt.axes(projection=ccrs.Robinson())
        ax.set_global()
        ax.coastlines(resolution="110m", linewidth=1)
        ax.gridlines(linestyle='--', color='black')

        # Set contour levels, then draw the plot and a colorbar
        clevs = np.arange(75000, 103366, 500)
        plt.contourf(lons_1, lats_1, T_1, clevs, transform=ccrs.PlateCarree(),
                     cmap=plt.cm.jet)
        plt.title('Surface Pressure at 12am 01.07.2020', size=14)
        cb = plt.colorbar(ax=ax, orientation="vertical", pad=0.02, aspect=16,
                          shrink=0.8)
        cb.set_label('Pa', size=12, rotation=0, labelpad=15)
        cb.ax.tick_params(labelsize=10)

        # Save the plot as a PNG image
        fig.savefig(destination_file, format=file_format, dpi=file_dpi)


# TODO: use numpy variables for speed and accuracy -- read the type from input
#  , save in dict

if __name__ == '__main__':
    with Dataset(my_example_nc_file, mode='r') as cdata:
        list()
        exit(0)
        lons: [float] = data.variables['lon'][:]
        lats: [float] = data.variables['lat'][:]
        T = data.variables['PS'][:, :, :]
        T: [float, float, float] = T[0, :, :]

        # Set the figure size, projection, and extent
        fig = plt.figure(figsize=(10, 6))
        ax = plt.axes(projection=ccrs.Robinson())
        ax.set_global()
        ax.coastlines(resolution="110m", linewidth=1)
        ax.gridlines(linestyle='--', color='black')

        # Set contour levels, then draw the plot and a colorbar
        clevs = np.arange(75000, 103366, 500)
        plt.contourf(lons_1, lats_1, T_1, clevs, transform=ccrs.PlateCarree(),
                     cmap=plt.cm.jet)
        plt.title('Surface Pressure at 12am 01.07.2020', size=14)
        cb = plt.colorbar(ax=ax, orientation="vertical", pad=0.02, aspect=16,
                          shrink=0.8)
        cb.set_label('Pa', size=12, rotation=0, labelpad=15)
        cb.ax.tick_params(labelsize=10)

        # Save the plot as a PNG image
        fig.savefig(destination_file, format=file_format, dpi=file_dpi)
