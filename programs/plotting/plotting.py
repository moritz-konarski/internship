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
file_format = "png"  # or pdf
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
    return (int(datetime_delta.days * meta_dict[
        'values_per_day'] + datetime_delta.seconds / 3600 / (
                        24 / meta_dict['values_per_day'])), end_datetime)


def heatmap(src_folder: str, graph_datetime: str, level: int):
    with open(src_folder + metadata_file_name, 'r') as f:
        meta_dict = json.load(f)
    src_file = src_folder + meta_dict['name'] + src_file_extension
    src = np.load(src_file, allow_pickle=True)

    time_index, graph_datetime = get_time_index(graph_datetime, meta_dict)

    if time_index < 0:
        print("Date too small, minimum is: " + str(
            meta_dict['begin_date']) + " 0")
        exit(-1)
    elif time_index > int(meta_dict['shape'][0]) - 1 and \
            meta_dict['last_day_inclusive']:
        print("Date too large, maximum is: " + str(meta_dict['end_date'])
              + " " + str((meta_dict['values_per_day'] - 1) /
                          meta_dict['values_per_day'] * 24))
        exit(-1)
    elif time_index > int(meta_dict['shape'][0]) - 1:
        print("Date too large, maximum is (last day is not included): " + str(
            meta_dict['end_date']) + " " + str(
            (meta_dict['values_per_day'] - 1) /
            meta_dict['values_per_day'] * 24))
        exit(-1)

    print("Plotting...")

    lev_str = ""
    data = None
    if meta_dict['lev_count'] == 0:
        data = src['data'][time_index, :, :]
    elif level < meta_dict['lev_count']:
        data = src['data'][time_index, level, :, :]
        lev_str = " " + str(src['lev'][level]) + " " + meta_dict['lev_units']
    else:
        print("Level must be less than: " + str(meta_dict['lev_count']))
        exit(-1)

    data_min = float(np.nanmin(data[:, :]))
    data_max = float(np.nanmax(data[:, :]))

    if np.isnan(data_min) and np.isnan(data_max):
        data_min = 0
        data_max = 1

    lats = src['lat']
    lons = src['lon']

    fig = plt.figure(figsize=(figure_width, figure_height))

    emin = meta_dict['lon_min']
    emax = meta_dict['lon_max']
    nmin = meta_dict['lat_min']
    nmax = meta_dict['lat_max']

    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_global()
    ax.set_extent([emin, emax, nmin, nmax], crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.BORDERS, linewidth=1.4)
    ax.gridlines(linestyle='--',
                 color='black',
                 draw_labels=True,
                 linewidth=0.5)

    res = float((data_max - data_min) / 20)

    clevs = np.arange(data_min, data_max + res, res, dtype=float)
    plt.contourf(lons,
                 lats,
                 data,
                 clevs,
                 transform=ccrs.PlateCarree(),
                 cmap=plt.cm.jet)

    cb = plt.colorbar(ax=ax,
                      orientation="vertical",
                      pad=0.08,
                      aspect=16,
                      shrink=0.8)

    cb.ax.tick_params(labelsize=10, pad=0.5)

    title = meta_dict['long_name'] + " on " \
            + graph_datetime.strftime("%d.%m.%Y %H:%M") + lev_str

    plt.title(title, size=18, loc='left', pad=10)
    cb.set_label(meta_dict['units'], size=12, rotation=90, labelpad=10)

    with open(title + '.' + file_format, 'wb') as f:
        fig.savefig(f, format=file_format, dpi=file_dpi,
                    transparent=is_background_transparent,
                    bbox_inches='tight', pad_inches=inch_padding)


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


def get_datetime_list(start: datetime, end: datetime, interval: int) -> [
    datetime]:
    delta = end - start

    date_list = []

    for day in range(delta.days):
        for hour in range(0, 24, interval):
            date_list.append(start + datetime.timedelta(days=day, hours=hour))
            # print(start + datetime.timedelta(days=day, hours=hour))

    for hour in range(0, int(delta.seconds / 3600) + 1, interval):
        date_list.append(
            start + datetime.timedelta(days=delta.days, hours=hour))
        # print(start + datetime.timedelta(days=delta.days,hours=hour))

    return date_list


def timeseries(src_folder: str, graph_datetime_start: str,
               graph_datetime_end: str, lats: str, lons: str, level: int):
    with open(src_folder + metadata_file_name, 'r') as f:
        meta_dict = json.load(f)
    src_file = src_folder + meta_dict['name'] + src_file_extension
    src = np.load(src_file, allow_pickle=True)

    start_time_index, start_graph_datetime = get_time_index(
        graph_datetime_start, meta_dict)
    end_time_index, end_graph_datetime = get_time_index(graph_datetime_end,
                                                        meta_dict)

    if start_time_index > end_time_index:
        print("End time must be after start time")
        exit(-1)

    if start_time_index < 0:
        print("Start date too small, minimum is: " + str(
            meta_dict['begin_date']) + " 0")
        exit(-1)
    elif end_time_index > int(meta_dict['shape'][0]) - 1 and \
            meta_dict['last_day_inclusive']:
        print("End date too large, maximum is: " + str(meta_dict['end_date'])
              + " " + str((meta_dict['values_per_day'] - 1) /
                          meta_dict['values_per_day'] * 24))
        exit(-1)
    elif end_time_index > int(meta_dict['shape'][0]) - 1:
        print(
            "End date too large, maximum is (last day is not included): " + str(
                meta_dict['end_date']) + " " + str(
                (meta_dict['values_per_day'] - 1) /
                meta_dict['values_per_day'] * 24))
        exit(-1)

    print("Plotting...")

    lat = find_closest_point_index(lats, src['lat'])
    lon = find_closest_point_index(lons, src['lon'])

    lev_str = ""
    data = None
    if meta_dict['lev_count'] == 0:
        data = src['data'][start_time_index:end_time_index + 1, lat, lon]
    elif level < meta_dict['lev_count']:
        data = src['data'][start_time_index:end_time_index + 1, level, lat, lon]
        lev_str = " at " + str(src['lev'][level]) + " " + meta_dict['lev_units']
    else:
        print("Level must be less than: " + str(meta_dict['lev_count']))
        exit(-1)

    data_min = float(np.nanmin(data[:]))
    data_max = float(np.nanmax(data[:]))

    if np.isnan(data_min) and np.isnan(data_max):
        data_min = 0
        data_max = 1

    if data_min < 0:
        data_min *= 1.05
    else:
        data_min *= 0.95

    if data_max < 0:
        data_max *= 0.95
    else:
        data_max *= 1.05

    plt.style.use('seaborn-whitegrid')

    fig = plt.figure(figsize=(figure_width, figure_height))

    ax = plt.axes()

    title = meta_dict['long_name'] + lev_str + " at (" + str(
        lats) + "N, " + str(lons) + "E)" + " from \n" \
            + start_graph_datetime.strftime("%d.%m.%Y %H:%M") + " to " + \
            end_graph_datetime.strftime("%d.%m.%Y %H:%M")

    dates = get_datetime_list(start_graph_datetime, end_graph_datetime,
                              int(24 / meta_dict['values_per_day']))

    if len(dates) / 8 < 3:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y %H'))
        plt.gca().xaxis.set_major_locator(
            mdates.HourLocator(byhour=[0, 3, 6, 9, 12, 15, 18, 21]))
    elif len(dates) / 8 < 6:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y %H'))
        plt.gca().xaxis.set_major_locator(
            mdates.HourLocator(byhour=[0, 6, 12, 18]))
    elif len(dates) / 8 <= 15:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    elif len(dates) / 8 > 15:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))
        # TODO: make this work when
    else:
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())

    ax.plot(dates, data)
    plt.gcf().autofmt_xdate()

    plt.title(title, size=18, loc='left', pad=20)

    plt.ylabel(meta_dict['units'])
    plt.xlabel("Dates")

    # TODO: change back to title
    with open('plot' + '.' + file_format, 'wb') as f:
        fig.savefig(f, format=file_format, dpi=file_dpi,
                    transparent=is_background_transparent,
                    bbox_inches='tight',
                    pad_inches=inch_padding)


if __name__ == '__main__':
    fire.Fire({
        "info": get_data_info,
        "heatmap": heatmap,
        "timeseries": timeseries
    })
