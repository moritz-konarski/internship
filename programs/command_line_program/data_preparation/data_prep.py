#!/bin/env python

import os
import re
import fire
import json
import numpy as np
from pathlib import Path
from netCDF4 import Dataset

src_files = "*.nc4"
tmp_file_ending = "_tmp.npz"
file_ending = ".npz"
dir_separator = "/"
tmp_metadata_file_name = "metadata_tmp.json"
metadata_file_name = "metadata.json"


def var_name_format(name: str) -> str:
    n = re.sub("_", " ", name)
    return " ".join(w.capitalize() for w in n.split())


def extract(src_path: str, dest_path: str, var_name: str):
    reg = r"{0}$".format(dir_separator)
    if not re.findall(reg, dest_path):
        dest_path += dir_separator + var_name + dir_separator
    else:
        dest_path += var_name + dir_separator
    os.makedirs(dest_path, exist_ok=True)

    print("Extracting " + var_name + "...")

    sorted_file_list = sorted(Path(src_path).glob(src_files))
    first_file = sorted_file_list[0]
    last_file = sorted_file_list[-1]

    data_file = dest_path + var_name + tmp_file_ending
    extract_and_save_data(sorted_file_list, data_file, var_name)

    dest_file = dest_path + tmp_metadata_file_name
    extract_metadata(dest_file, first_file, last_file, data_file, var_name)

    replace_fill_value(dest_path)


def extract_and_save_data(file_list: [str], dest_path: str, var_name: str):
    data = None
    for (i, part) in enumerate(file_list):
        filepath = os.path.join(part)
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

    data = data.astype(np.float32, casting='safe')
    time = time.astype(np.int32, casting='safe')
    lat = lat.astype(np.float64, casting='safe')
    lon = lon.astype(np.float64, casting='safe')
    lev = lev.astype(np.float64, casting='safe')

    with open(dest_path, 'wb') as f:
        np.savez_compressed(f,
                            data=data,
                            time=time,
                            lat=lat,
                            lon=lon,
                            lev=lev,
                            allow_pickle=True)


def replace_fill_value(path: str):
    with open(path + tmp_metadata_file_name, 'r') as f:
        meta_dict = json.load(f)

    if meta_dict['data_max'] == meta_dict['fill_value']:
        d = np.load(path + meta_dict['name'] + tmp_file_ending,
                    allow_pickle=True)
        if meta_dict['lev_count'] == 0:
            new_d = np.where(d['data'][:, :, :] != meta_dict['fill_value'],
                             d['data'][:, :, :], np.NaN)
        else:
            new_d = np.where(d['data'][:, :, :, :] != meta_dict['fill_value'],
                             d['data'][:, :, :, :], np.NaN)

        with open(path + meta_dict['name'] + file_ending, 'wb') as f:
            np.savez_compressed(f,
                                data=new_d,
                                time=d['time'],
                                lat=d['lat'],
                                lon=d['lon'],
                                lev=d['lev'],
                                allow_pickle=True)
        os.remove(path + meta_dict['name'] + tmp_file_ending)

        if len(new_d.shape) == 4:
            data_max = float(np.nanmax(new_d[:, :, :, :]))
            data_min = float(np.nanmin(new_d[:, :, :, :]))
        else:
            data_max = float(np.nanmax(new_d[:, :, :]))
            data_min = float(np.nanmin(new_d[:, :, :]))
        meta_dict['data_max'] = data_max
        meta_dict['data_min'] = data_min

        with open(path + metadata_file_name, 'w') as f:
            json.dump(meta_dict, f)
        os.remove(path + tmp_metadata_file_name)

    else:
        os.rename(path + meta_dict['name'] + tmp_file_ending,
                  path + meta_dict['name'] + file_ending)
        os.rename(path + tmp_metadata_file_name, path + metadata_file_name)


def extract_metadata(dest_file: str, first_file: Path, last_file: Path,
                     data_file: str, var: str):
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
    var_info_list = []
    with Dataset(path, 'r') as d:
        for var in d.variables.keys():
            var_info_list.append(
                (var, d.variables[var].long_name, d.variables[var].units))
    for (var, name, unit) in var_info_list:
        print("{0:6s} {1:15s} {2:s}".format(var, unit, name))


def get_all_var_names(path: Path) -> [str]:
    var_info_list = []
    with Dataset(path, 'r') as d:
        for var in d.variables.keys():
            if var != 'time' and var != 'lat' and var != 'lon' and var != 'lev':
                var_info_list.append(var)
    return var_info_list


def extract_all(src_path: str, dest_path: str):
    var_name_src_file = sorted(Path(src_path).glob(src_files))[0]
    var_name_list = get_all_var_names(var_name_src_file)
    print(var_name_list)
    for var_name in var_name_list:
        extract(src_path, dest_path, var_name)


if __name__ == '__main__':
    fire.Fire({
        "list": print_all_vars,
        "extract": extract,
        "extract-all": extract_all
    })
