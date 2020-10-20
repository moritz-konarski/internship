#!/bin/env python

import os
import re
import sys
import fire
import json
import numpy as np
from pathlib import Path
from netCDF4 import Dataset


def var_name_format(name: str) -> str:
    n = re.sub("_", " ", name)
    return " ".join(w.capitalize() for w in n.split())


def extract(src_path: str, dest_path: str, var_name: str):
    if not re.findall(r"/$", dest_path):
        dest_path += "/" + var_name + "/"
    else:
        dest_path += var_name + "/"
    os.makedirs(dest_path, exist_ok=True)

    sorted_file_list = sorted(Path(src_path).glob("*.nc4"))
    n_files = len(sorted_file_list)
    first_file = sorted_file_list[0]
    last_file = sorted_file_list[-1]

    data_file = dest_path + var_name + ".npz"
    extract_and_save_data(sorted_file_list, data_file, var_name)

    dest_file = dest_path + "metadata.json"
    extract_metadata(dest_file, first_file, last_file, data_file, var_name)

    replace_fill_value(dest_path)


def extract_and_save_data(file_list: [str], dest_path: str, var_name: str):
    n_files = len(file_list)
    data = time = lat = lon = lev = None
    for (i, part) in enumerate(file_list):
        filepath = os.path.join(part)
        #print(str(i + 1) + "/" + str(n_files))
        with Dataset(filepath, 'r') as d:
            if data is None:
                data = np.asarray(d.variables[var_name])
            else:
                data = np.append(data,
                                 np.asarray(d.variables[var_name]),
                                 axis=0)
    first_file = file_list[0]
    filepath = os.path.join(first_file)
    with Dataset(filepath, 'r') as d:
        time = np.asarray(d.variables['time'])
        lat = np.asarray(d.variables['lat'])
        lon = np.asarray(d.variables['lon'])
        lev = np.asarray(d.variables['lev'])

    print("Converting data types...")
    data = data.astype(np.float32, casting='safe')
    time = time.astype(np.int32, casting='safe')
    lat = lat.astype(np.float64, casting='safe')
    lon = lon.astype(np.float64, casting='safe')
    lev = lev.astype(np.float64, casting='safe')

    print("Writing to file...")
    with open(dest_path, 'wb') as f:
        np.savez_compressed(f, data=data, time=time, lat=lat, lon=lon, \
                lev=lev, allow_pickle=True)


def replace_fill_value(path: str):
    meta_dict = None
    with open(path + "metadata.json", 'r') as f:
        meta_dict = json.load(f)

    #print("max == fill: " + \
    #        str(meta_dict['data_max'] == meta_dict['fill_value']))

    #print("max : " + str(meta_dict['data_max']))
    #print("fill: " + str(meta_dict['fill_value']))

    if meta_dict['data_max'] == meta_dict['fill_value']:
        print("Converting fill values to NaN...")
        d = np.load(path + meta_dict['name'] + ".npz", allow_pickle=True)
        if meta_dict['lev_count'] == 0:
            new_d = np.where(d['data'][:,:,:] != meta_dict['fill_value'], \
                    d['data'][:,:,:], np.NaN)
        else:
            new_d = np.where(d['data'][:,:,:,:] != meta_dict['fill_value'], \
                    d['data'][:,:,:,:], np.NaN)

        with open(path + meta_dict['name'] + ".npz", 'wb') as f:
            np.savez_compressed(f, data=new_d, time=d['time'],       \
                    lat=d['lat'], lon=d['lon'], lev=d['lev'],  \
                    allow_pickle=True)


def extract_metadata(dest_file: str, first_file: str, last_file: str,
                     data_file: str, var: str):
    print("Extracting metadata...")
    name = long_name = std_name = units = shape = time_steps = None
    begin_date = end_date = lat_min = lat_max = lon_min = lon_max = None
    lev_units = lat_units = lon_units = data_min = data_max = None
    lev_min = lev_max = fill_value = None
    with Dataset(first_file, 'r') as d:
        name = str(d.variables[var].name)
        long_name = var_name_format(d.variables[var].long_name)
        std_name = var_name_format(d.variables[var].standard_name)
        units = str(d.variables[var].units)
        fill_value = float(d.variables[var]._FillValue)
        lat_units = str(d.variables['lat'].units)
        lon_units = str(d.variables['lon'].units)
        lev_units = str(d.variables['lev'].units)
        begin_date = str(d.RangeBeginningDate)
    with Dataset(last_file, 'r') as d:
        end_date = str(d.RangeEndingDate)

    d = np.load(data_file, allow_pickle=True)
    shape = d['data'].shape
    time_steps = int(d['time'].shape[0])
    lat_min = float(d['lat'].min())
    lat_max = float(d['lat'].max())
    lon_min = float(d['lon'].min())
    lon_max = float(d['lon'].max())
    lev_min = float(d['lev'].min())
    lev_max = float(d['lev'].max())
    if len(shape) == 4:
        data_max = float(d['data'][:, :, :, :].max())
        data_min = float(d['data'][:, :, :, :].min())
    else:
        data_max = float(d['data'][:, :, :].max())
        data_min = float(d['data'][:, :, :].min())

    info_dict = {
        "name": name,
        "long_name": long_name,
        "std_name": std_name,
        "units": units,
        "shape": shape,
        "data_max": data_max,
        "data_min": data_min,
        "values_per_day": time_steps,
        "day_count": int(shape[0] / time_steps),
        "begin_date": begin_date,
        "end_date": end_date,
        "last_day_inclusive": True,
        "lat_min": lat_min,
        "lat_max": lat_max,
        "lat_count": int(shape[-2]),
        "lat_units": lat_units,
        "lon_min": lon_min,
        "lon_max": lon_max,
        "lon_count": int(shape[-1]),
        "lon_units": lon_units,
        "lev_min": lev_min,
        "lev_max": lev_max,
        "lev_count": 0 if len(shape) != 4 else int(shape[1]),
        "lev_units": lev_units,
        "fill_value": fill_value
    }
    with open(dest_file, 'w') as f:
        json.dump(info_dict, f)


def print_all_vars(path: str):
    l = []
    with Dataset(path, 'r') as d:
        for var in d.variables.keys():
            l.append((var, d.variables[var].long_name, d.variables[var].units))
    for (var, name, unit) in l:
        print("{0:6s} {1:15s} {2:s}".format(var, unit, name))


if __name__ == '__main__':
    fire.Fire({"list": print_all_vars, "extract": extract})
