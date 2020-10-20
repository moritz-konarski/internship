#!/bin/env python

import os
import re
import sys
import fire
import json
import pprint
import datetime
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


file_dpi = 300


def get_data_info(src_folder: str):
    with open(src_folder + "metadata.json", 'r') as f:
        info_dict = json.load(f)
    pprint.PrettyPrinter(indent=4, sort_dicts=False).pprint(info_dict)


def get_time_index(src_folder: str, graph_datetime: str, meta_dict) -> (int,
        datetime):
    start_datetime = \
        datetime.datetime.strptime(meta_dict['begin_date'], '%Y-%m-%d')
    end_datetime = \
        datetime.datetime.strptime(graph_datetime, '%Y-%m-%d %H')
    datetime_delta = end_datetime - start_datetime
    return (int(datetime_delta.days * meta_dict['values_per_day'] 
        + datetime_delta.seconds / 3600 / (24 / meta_dict['values_per_day'])),
        end_datetime)


def heatmap(src_folder: str, name: str, graph_datetime: str, level: int):
    meta_dict = None
    with open(src_folder + "metadata.json", 'r') as f:
        meta_dict = json.load(f)
    src_file = src_folder + meta_dict['name'] + ".npz"
    src = np.load(src_file, allow_pickle=True)
    
    time_index, graph_datetime = get_time_index(src_folder, graph_datetime, \
            meta_dict)

    if time_index < 0:
        print("Date too small, minimum is: " + str(meta_dict['begin_date'])
                + " 0")
        exit(-1)
    elif time_index > int(meta_dict['shape'][0])-1 and \
            meta_dict['last_day_inclusive']:
        print("Date too large, maximum is: " + str(meta_dict['end_date'])
                + " 21")
        exit(-1)
    elif time_index > int(meta_dict['shape'][0])-1:
        print("Date too large, maximum is (last day is not included): " \
                + str(meta_dict['end_date']) + " 21")
        exit(-1)

    print("Plotting...")
    if meta_dict['lev_count'] == 0:
        data = src['data'][time_index,:,:]
        print(data.shape)
    elif level < meta_dict['lev_count']:
        data = src['data'][time_index, level,:,:]
        print(data.shape)
    else:
        print("Level must be less than: " + str(meta_dict['lev_count']))
        exit(-1)

    data_min = float(data[:,:].min())
    print(data_min)
    #print(data_min.shape)
    data_max = float(data[:,:].max())
    print(data_max)
    #print(data_max.shape)

    lats = src['lat']
    lons = src['lon']

    # Set the figure size, projection, and extent
    fig = plt.figure(figsize=(10, 6))

    emin = meta_dict['lon_min']
    emax = meta_dict['lon_max']
    nmin = meta_dict['lat_min']
    nmax = meta_dict['lat_max']

    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_global()
    ax.set_extent([emin, emax, nmin, nmax], crs=ccrs.PlateCarree())   
    ax.add_feature(cfeature.BORDERS, linewidth=1.4)
    ax.gridlines(linestyle='--', color='black', draw_labels=True,
                 linewidth=0.5)

    res = float((data_max - data_min) / 20)

    # Set contour levels, then draw the plot and a colorbar
    clevs = np.arange(data_min, data_max+res, res, dtype=float)
    plt.contourf(lons, lats, data, clevs, transform=ccrs.PlateCarree(),
                 cmap=plt.cm.jet)

    cb = plt.colorbar(ax=ax, orientation="vertical", pad=0.02, aspect=16,
                      shrink=0.8)

    cb.ax.tick_params(labelsize=10)

    title = "Heat Map of " + meta_dict['long_name'] + " on " \
        + str(graph_datetime)

    plt.title(title, size=14)
    cb.set_label(meta_dict['units'], size=12, rotation=0, labelpad=35)

    with open(name+".png", 'wb') as f:
        fig.savefig(f, format='png', dpi=file_dpi)

def timeseries(src_folder: str, lat: float, lon: float):
    pass

def graph_var(src_file: str, dest_file:str):
    pass
        
if __name__ == '__main__':
    fire.Fire({
        "graph": graph_var,
        "info": get_data_info,
        "heatmap": heatmap
    })


def create_graph(var: str, name: str):
    with Dataset(my_example_nc_file, mode='r') as data:
        lons: [float] = data.variables['lon'][:]
        lats: [float] = data.variables['lat'][:]

        min, max = find_range(var)

        d = data.variables[var][:, :, :]

        d: [float, float, float] = d[0, :, :]

        v_max = d[:].max()
        v_min = var[:].min()

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
