#!/bin/env python

import fire
import json
import pprint
import datetime
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

figure_width = 9.5
figure_height = 6
file_dpi = 400
file_format = 'pdf'
is_background_transparent = True
inch_padding = 0
metadata_file_name = "metadata.json"
src_file_extension = ".npz"


def get_time_index(graph_datetime: str, meta_dict) -> (int, datetime):
    start_datetime = datetime.datetime.strptime(meta_dict['begin_date'],
                                                '%Y-%m-%d')
    end_datetime = datetime.datetime.strptime(graph_datetime, '%Y-%m-%d %H')
    datetime_delta = end_datetime - start_datetime
    return (int(datetime_delta.days * meta_dict['values_per_day'] +
                datetime_delta.seconds / 3600 /
                (24 / meta_dict['values_per_day'])), end_datetime)


def heatmap(src_folder: str, graph_datetime: str, level: int):
    with open(src_folder + metadata_file_name, 'r') as f:
        meta_dict = json.load(f)
    src_file = src_folder + meta_dict['name'] + src_file_extension
    src = np.load(src_file, allow_pickle=True)

    time_index, graph_datetime = get_time_index(graph_datetime, meta_dict)

    if time_index < 0:
        print("Date too small, minimum is: " + str(meta_dict['begin_date']) +
              " 0")
        exit(-1)
    elif time_index > int(meta_dict['shape'][0]) - 1 and \
            meta_dict['last_day_inclusive']:
        print("Date too large, maximum is: " + str(meta_dict['end_date']) +
              " " + str((meta_dict['values_per_day'] - 1) /
                        meta_dict['values_per_day'] * 24))
        exit(-1)
    elif time_index > int(meta_dict['shape'][0]) - 1:
        print("Date too large, maximum is (last day is not included): " +
              str(meta_dict['end_date']) + " " +
              str((meta_dict['values_per_day'] - 1) /
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

    res = float((data_max - data_min) / 20)

    clevs = np.arange(data_min, data_max + res, res, dtype=float)
    plt.contourf(lons,
                 lats,
                 data,
                 clevs,
                 transform=ccrs.PlateCarree(),
                 cmap=plt.cm.jet)

    title = "Title Image " + meta_dict['long_name'] + "-" \
            + graph_datetime.strftime("%d.%m.%Y %H:%M") + lev_str

    with open(title + '.' + file_format, 'wb') as f:
        fig.savefig(f,
                    format=file_format,
                    dpi=file_dpi,
                    transparent=is_background_transparent,
                    bbox_inches='tight',
                    pad_inches=inch_padding)


if __name__ == '__main__':
    fire.Fire({
        "make": heatmap,
    })
