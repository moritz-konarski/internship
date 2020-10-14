#!/bin/env python

import os
import re
import sys
import fire
import json
import numpy as np
from pathlib import Path
from netCDF4 import Dataset


def extract_var(src_path: str, dest_path: str, var_name: str):
    if not re.findall(r"/$", dest_path):
        dest_path += "/" + var_name + "/"
    else:
        dest_path += var_name + "/"
    os.makedirs(dest_path, exist_ok=True)

    sorted_file_list = sorted(Path(src_path).glob("*.nc4"))
    n_files = len(sorted_file_list)
    first_file = sorted_file_list[0]
    last_file = sorted_file_list[-1]

    n_files = len(sorted_file_list)
    # get data from files
    with open(dest_path + var_name + ".npz", 'wb') as f:
        data = None
        for (i, part) in enumerate(sorted_file_list):
            filepath = os.path.join(part)
            print(str(i+1) + "/" + str(n_files))
            with Dataset(filepath, 'r') as d:
                if data is None:
                    data = np.asarray(d.variables[var_name])
                else:
                    data = np.append(data, np.asarray(d.variables[var_name]), 
                            axis=0)
        time = None
        lats = None
        lons = None
        part = sorted_file_list[0]
        filepath = os.path.join(part)
        with Dataset(filepath, 'r') as d:
            time = np.asarray(d.variables['time'])
            lats = np.asarray(d.variables['lat'])
            lons = np.asarray(d.variables['lon'])
        print("Writing to file...")
        np.savez_compressed(f, data=data, time=time, lat=lats, lon=lons, 
            allow_pickle=True)
    
    with open(dest_path + "metadata.json", 'w') as f:
        json.dump(extract_metadata(first_file, last_file, var_name, n_files), f)


def get_var_info_list(path: str) -> [str, str, str]:
    """
    List all variables, their names, units in the specified file.
    """
    list = []
    with Dataset(path, 'r') as d:
        for var in d.variables.keys():
            list.append((var, d.variables[var].long_name, 
                    d.variables[var].units))#, d.variables[var].dimension))
        print(d.variables)
    return list


def print_all_vars(path: str):
    for (var, name, unit) in get_var_info_list(path):
        print("{0:6s} {1:15s} {2:s}".format(var, unit, name))


# add count of the days
def extract_metadata(first_file: str, last_file: str, var: str, count: int) -> dict:
    name = None
    long_name = None
    std_name = None
    units = None
    shape = None
    time_shape = None
    begin_date = None
    end_date = None
    lat_min = None
    lat_max = None
    lon_min = None
    lon_max = None
    with Dataset(first_file, 'r') as d:
        lat_min = float(d.variables['lat'][0])
        lat_max = float(d.variables['lat'][-1])
        lat_count = len(d.variables['lat'])
        lon_min = float(d.variables['lon'][0])
        lon_max = float(d.variables['lon'][-1])
        lon_count = len(d.variables['lon'])
        name = d.variables[var].name
        long_name = re.sub("_", " ", d.variables[var].long_name)
        std_name =  re.sub("_", " ", d.variables[var].standard_name)
        units = d.variables[var].units
        shape = d.variables[var].shape
        time_shape = d.variables['time'].shape
        begin_date = d.RangeBeginningDate
    with Dataset(last_file, 'r') as d:
        end_date = d.RangeEndingDate
    info_dict = {
            "name" : name,
            "long_name" : long_name,
            "std_name" : std_name, 
            "units" : units,
            "shape" : shape,
            "level_count" : 0 if len(shape) != 4 else int(shape[2]),
            "values_per_day" : int(time_shape[0]),
            "day_count" : count,
            "begin_date" : begin_date,
            "end_date" : end_date,
            "lat_min" : lat_min,
            "lat_max" : lat_max,
            "lat_count" : lat_count,
            "lon_min" : lon_min,
            "lon_max" : lon_max,
            "lon_count" : lon_count,
        }
    return info_dict


if __name__ == '__main__':
    fire.Fire({
        "list": print_all_vars,
        "extract": extract_var
    })
