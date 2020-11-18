#!/bin/env python

import fire
import json
import pprint
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import cartopy.crs as ccrs
import cartopy.feature as cfeature

figure_width = 9.5
figure_height = 6
file_dpi = 300
file_format = "pdf"  # or pdf
is_background_transparent = False
inch_padding = 0.1
metadata_file_name = "metadata.json"
src_file_extension = ".npz"


def get_data_info(src_folder: str):
    with open(src_folder + metadata_file_name, 'r') as f:
        info_dict = json.load(f)
    pprint.PrettyPrinter(indent=4, sort_dicts=False).pprint(info_dict)


def get_time_index(graph_datetime: str, meta_dict) -> (int, datetime):
    start_datetime = datetime.datetime.strptime(meta_dict['begin_date'],
                                                '%Y-%m-%d')
    end_datetime = datetime.datetime.strptime(graph_datetime, '%Y-%m-%d %H')
    datetime_delta = end_datetime - start_datetime
    return (int(datetime_delta.days * meta_dict['values_per_day'] +
                datetime_delta.seconds / 3600 /
                (24 / meta_dict['values_per_day'])), end_datetime)

def find_closest_point_index(given: str, options) -> int:
    val = float(given)
    min = np.nanmin(options)
    max = np.nanmax(options)

    if val > max or val < min:
        print("Latitute or Longitute out of range")
        exit(-1)

    best_index = -1
    min_diff = max
    for (i, opt) in enumerate(options):
        if abs(opt - val) < min_diff:
            best_index = i

    return best_index


def get_datetime_list(start: datetime, end: datetime,
                      interval: int) -> [datetime]:
    delta = end - start

    date_list = []

    for day in range(delta.days):
        for hour in range(0, 24, interval):
            date_list.append(start + datetime.timedelta(days=day, hours=hour))
            # print(start + datetime.timedelta(days=day, hours=hour))

    for hour in range(0, int(delta.seconds / 3600) + 1, interval):
        date_list.append(start +
                         datetime.timedelta(days=delta.days, hours=hour))
        # print(start + datetime.timedelta(days=delta.days,hours=hour))

    return date_list


def timeseries(src_folder: str, graph_datetime_start: str,
        lats: str, lons: str, is_log: bool):
    with open(src_folder + metadata_file_name, 'r') as f:
        meta_dict = json.load(f)
    src_file = src_folder + meta_dict['name'] + src_file_extension
    src = np.load(src_file, allow_pickle=True)

    start_time_index, start_graph_datetime = get_time_index(
        graph_datetime_start, meta_dict)

    print("Plotting...")

    lat = find_closest_point_index(lats, src['lat'])
    lon = find_closest_point_index(lons, src['lon'])

    lev_str = ""
    data = src['data'][start_time_index, :, lat, lon]

    plt.style.use('seaborn-whitegrid')

    fig = plt.figure(figsize=(figure_width, figure_height))

    ax = plt.axes()

    if not is_log:
        title = meta_dict['long_name'] + lev_str + " vertical structure at (" + str(
            lats) + "N, " + str(lons) + "E)" + "\non " \
                + start_graph_datetime.strftime("%d.%m.%Y %H:%M")
    else:
        title = meta_dict['long_name'] + lev_str + " vertical structure at (" + str(
            lats) + "N, " + str(lons) + "E)" + "\non " \
                + start_graph_datetime.strftime("%d.%m.%Y %H:%M") + \
                " log scale"
    # this works
    ax.plot(data, src['lev'])


    plt.title(title, size=18, loc='left', pad=20)

    plt.xlabel(meta_dict['units'])
    plt.ylabel("Pressure hPa")
    if is_log:
        plt.yscale("log")
    
    plt.gca().invert_yaxis()
    
    if is_log:
        with open('plot_log' + '.' + file_format, 'wb') as f:
            fig.savefig(f,
                        format=file_format,
                        dpi=file_dpi,
                        transparent=is_background_transparent,
                        bbox_inches='tight',
                        pad_inches=inch_padding)
    else:
        with open('plot' + '.' + file_format, 'wb') as f:
            fig.savefig(f,
                        format=file_format,
                        dpi=file_dpi,
                        transparent=is_background_transparent,
                        bbox_inches='tight',
                        pad_inches=inch_padding)


if __name__ == '__main__':
    fire.Fire({
        "info": get_data_info,
        "timeseries": timeseries
    })
