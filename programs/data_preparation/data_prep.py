#!/bin/env python

import os
import re
import sys
import fire
import json
import numpy as np
from pathlib import Path
from netCDF4 import Dataset


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


def extract_and_save_data(file_list: [str], dest_path: str, var_name: str):
    n_files = len(file_list)
    data = time = lat = lon = None
    for (i, part) in enumerate(file_list):
        filepath = os.path.join(part)
        print(str(i+1) + "/" + str(n_files))
        with Dataset(filepath, 'r') as d:
            if data is None:
                data = np.asarray(d.variables[var_name])
            else:
                data = np.append(data, np.asarray(d.variables[var_name]), 
                        axis=0)
    first_file = file_list[0]
    filepath = os.path.join(first_file)
    with Dataset(filepath, 'r') as d:
        time = np.asarray(d.variables['time'])
        lat = np.asarray(d.variables['lat'])
        lon = np.asarray(d.variables['lon'])
    print("Writing to file...")
    with open(dest_path, 'wb') as f:
        np.savez_compressed(f, data=data, time=time, lat=lat, lon=lon, 
            allow_pickle=True)
    
def extract_metadata(dest_file: str, first_file: str, last_file: str,
        data_file: str, var: str):
    print("Extracting metadata...")
    name = long_name = std_name = units = shape = time_steps = None
    begin_date = end_date = lat_min = lat_max = lon_min = lon_max = None
    data_min = data_max = None
    with Dataset(first_file, 'r') as d:
        name = d.variables[var].name
        long_name = re.sub("_", " ", d.variables[var].long_name)
        std_name =  re.sub("_", " ", d.variables[var].standard_name)
        units = d.variables[var].units
        begin_date = d.RangeBeginningDate
    with Dataset(last_file, 'r') as d:
        end_date = d.RangeEndingDate

    d = np.load(data_file, allow_pickle=True)
    shape = d['data'].shape
    time_steps = int(d['time'].shape[0])
    lat_min = float(d['lat'][0])
    lat_max = float(d['lat'][-1])
    lon_min = float(d['lon'][0])
    lon_max = float(d['lon'][-1])
    if len(shape) == 4:
        data_max = float(d['data'][:,:,:,:].max())
        data_min = float(d['data'][:,:,:,:].min())
    else:
        data_max = float(d['data'][:,:,:].max())
        data_min = float(d['data'][:,:,:].min())

    info_dict = {
            "name" : name,
            "long_name" : long_name,
            "std_name" : std_name, 
            "units" : units,
            "shape" : shape,
            "data_max": data_max,
            "data_min": data_min,
            "level_count" : 0 if len(shape) != 4 else int(shape[1]),
            "values_per_day" : time_steps,
            "day_count" : int(shape[0] / time_steps),
            "begin_date" : begin_date,
            "end_date" : end_date,
            "last_day_inclusive" : True,
            "lat_min" : lat_min,
            "lat_max" : lat_max,
            "lat_count" : int(shape[-2]),
            "lon_min" : lon_min,
            "lon_max" : lon_max,
            "lon_count" : int(shape[-1])
        }
    with open(dest_file, 'w') as f:
        json.dump(info_dict, f)


def print_all_vars(path: str):
    l = []
    with Dataset(path, 'r') as d:
        for var in d.variables.keys():
            l.append((var, d.variables[var].long_name, 
                    d.variables[var].units))
    for (var, name, unit) in l:
        print("{0:6s} {1:15s} {2:s}".format(var, unit, name))


if __name__ == '__main__':
    fire.Fire({
        "list": print_all_vars,
        "extract": extract
    })
