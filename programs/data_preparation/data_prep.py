#!/bin/env python

import os
import re
import sys
import fire
import numpy as np
from pathlib import Path
from netCDF4 import Dataset


def extract_var(src_path: str, dest_path: str, var_name: str):
    if not re.findall(r"/$", dest_path):
        dest_path + "/"
    if not os.path.exists(dest_path):
        os.mkdir(dest_path)

    with open(dest_path + var_name + ".npz", 'wb') as f:
        data = None
        for part in sorted(Path(src_path).glob("*.nc4")):
            filepath = os.path.join(part)
            print(filepath)
            with Dataset(filepath, 'r') as d:
                if data is None:
                    data = np.asarray(d.variables[var_name])
                else:
                    data = np.append(data, np.asarray(d.variables[var_name]), 
                            axis=0)
        time = None
        lats = None
        lons = None
        part = sorted(Path(src_path).glob("*.nc4"))[0]
        filepath = os.path.join(part)
        with Dataset(filepath, 'r') as d:
            time = np.asarray(d.variables['time'])
            lats = np.asarray(d.variables['lat'])
            lons = np.asarray(d.variables['lon'])
        np.savez_compressed(f, data=data, time=time, lat=lats, lon=lons, 
            allow_pickle=True)


def extract_time_lat_lon(src_path: str, dest_path: str):
    if not re.findall(r"/$", dest_path):
        dest_path + "/"
    if not os.path.exists(dest_path):
        os.mkdir(dest_path)

    with open(dest_path + "time.npz", 'wb') as f:
        part = sorted(Path(src_path).glob("*.nc4"))[0]
        filepath = os.path.join(part)
        print(filepath)
        with Dataset(filepath, 'r') as d:
            data = np.asarray(d.variables['time'])
            print(data.shape)
        np.savez_compressed(f, data, allow_pickle=True)

    with open(dest_path + "lat.npz", 'wb') as f:
        part = sorted(Path(src_path).glob("*.nc4"))[0]
        filepath = os.path.join(part)
        print(filepath)
        with Dataset(filepath, 'r') as d:
            data = np.asarray(d.variables['lat'])
            print(data.shape)
        np.savez_compressed(f, data, allow_pickle=True)

    with open(dest_path + "lon.npz", 'wb') as f:
        part = sorted(Path(src_path).glob("*.nc4"))[0]
        filepath = os.path.join(part)
        print(filepath)
        with Dataset(filepath, 'r') as d:
            data = np.asarray(d.variables['lon'])
            print(data.shape)
        np.savez_compressed(f, data, allow_pickle=True)

    #with Dataset(path, 'r') as d:
    #    for var_name in var_list:
    #        var = np.asarray(d.variables[var_name])
    #        file_name = os.path.realpath(store_path) + '/' + date + "_"     \
    #                + var_name + ".npz"
    #        with open(file_name, 'wb') as f:
    #            np.savez_compressed(f, var, allow_pickle=True)

    #with Dataset(path, 'r') as d:
    #    var = np.array(d.variables[var_name])
    #    np.save(os.path.realpath(store_path) + '/' + var_name + '.npy', var,
    #            allow_pickle=True)

def test_file(src_path: str):
    src = np.load(src_path, allow_pickle=True)
    print(src['arr_0'].shape)


# TODO: make sure that only the files that have dates are used here
# it should not try to load itself in the process
def concat(name: str, path: str, dest: str):
    with open(dest, 'wb') as f:
        for part in Path(path).glob("*" + name + ".npz"):
            filepath = os.path.join(part)
            print(filepath)
            dataArray = np.load(filepath, allow_pickle=True)
            #print(dataArray['arr_0'])
            np.savez_compressed(f, dataArray['arr_0'], allow_pickle=True)


def extract_all(path: str, store_path: str):
    var_list = get_var_name_list(path)
    if not re.findall(r"/$", store_path):
        store_path + "/"
    if not os.path.exists(store_path):
        os.mkdir(store_path)
    date = get_date_range(path)
    with Ds(path, 'r') as d:
        for var_name in var_list:
            var = np.asarray(d.variables[var_name])
            file_name = os.path.realpath(store_path) + '/' + date + "_"     \
                    + var_name + ".npz"
            with open(file_name, 'wb') as f:
                np.savez_compressed(f, var, allow_pickle=True)


def create_metadata_file(data: str, dest: str, var_list: str):
    pass


def get_var_info_list(path: str) -> [str, str, str]:
    """
    List all variables, their names, uiniets in the specified file.
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


def get_date_range(path: str) -> str:
    with Ds(path, 'r') as d:
        return str(d.RangeBeginningDate) + "_" + str(d.RangeEndingDate)


if __name__ == '__main__':
    fire.Fire({
        "list": print_all_vars,
        "extract": extract_var,
        "meta": extract_time_lat_lon,
        "test": test_file
    })

    #concat('_PS', './test/', './test/PS.npz')
    #concat('_H', './test/', './test/H.npz')
    #concat('_O3', './test/', './test/O3.npz')
    #concat('_EPV', './test/', './test/EPV.npz')
    #check_src_path('../var_extract')
    #check_dest_path('lol')
    #check_dest_path('hi')


def convert_path(str_path: str) -> Path:
    """
    Takes a string path as input and returns a Path object
    """
    return Path(str_path)


def check_src_path(str_path: str) -> Path:
    """
    Checks if the supplied source directory exists and is not empty
    """
    path = convert_path(str_path)

    if os.path.exists(path) and os.path.isdir(path):
        if not os.listdir(path):
            print("Source directory is empty: " + str(path), file=sys.stderr)
            sys.exit(1)
        else:
            return path
    else:
        print("Source directory don't exists: " + str(path), file=sys.stderr)
        sys.exit(1)


def check_dest_path(str_path: Path):
    """
    Checks if the supplied source directory exists
    """
    path = convert_path(str_path)

    if os.path.exists(path) and not os.path.isdir(path):
        print("Destination is not a directory" + str(path), file=sys.stderr)
        sys.exit(1)
    elif os.path.exists(path) and os.path.isdir(path):
        return path
    else:
        os.mkdir(path)
        return path

def var_exists(path: Path, var_name: str) -> bool:
    """
    Checks if the selected file contains the desired variable
    """


def get_var_name_list(path: str) -> [str]:
    """
    List all variables in the specified file.
    """
    list = []
    with Dataset(path, 'r') as d:
        for var in d.variables.keys():
            list.append(var + "\t" + d.variables[var].units + ", " + 
                    d.variables[var].long_name)
    return list
