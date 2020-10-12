#!/bin/env python

import os
import re
import sys
import fire
import numpy as np
import matplotlib.pyplot as plt

file_dpi = 500

def graph_var(src_file: str, dest_file:str):
    with open(dest_file+".png", 'wb') as f:
        # TODO: have if statement for 
        src = np.load(src_file, allow_pickle=True)
        data = src['data'][:,10,10]

        fig = plt.figure(figsize=(10, 6))
        
        plt.plot(data)
        plt.title("Surface Pressure Time Series", size=14)

        fig.savefig(f, format='png', dpi=file_dpi)

if __name__ == '__main__':
    fire.Fire({
        "graph": graph_var
    })


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


def get_var_name_list() -> [str]:
    list = []
    with Dataset(my_example_nc_file, mode='r') as data:
        for var in data.variables.keys():
            list.append(var)
    return list


def list_var_names():
    for var in get_var_name_list():
        print(var)


def extract_vars_into_files(list: [str], filepath: str):
    for var in list:
        os.system("ncks -v " +
                  var + " " +
                  filepath + "20200701.nc4 " +
                  filepath + "20200701_" + var + ".nc4")


def find_range(var_name):
    with Dataset(my_example_nc_file, mode='r') as data:
        var = data.variables[var_name]
        max = var[:].max()
        min = var[:].min()
    return min, max
