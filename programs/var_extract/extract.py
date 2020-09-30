#!/bin/env python


import os
import re
import fire
from pathlib import Path
from netCDF4 import Dataset as Ds
import numpy as np


def extract_var_from_file(path: str, store_path: str, var_name: str):
    if not re.findall(r"/$", store_path):
        store_path + "/"
    if not os.path.exists(store_path):
        os.mkdir(store_path)
    with Ds(path, 'r') as d:
        var = np.array(d.variables[var_name])
        np.save(os.path.realpath(store_path) + '/' + var_name + '.npy', var,
                allow_pickle=True)


def extract_all(path: str, store_path: str):
    var_list = get_var_name_list(path)
    if not re.findall(r"/$", store_path):
        store_path + "/"
    if not os.path.exists(store_path):
        os.mkdir(store_path)
    date = get_date_range(path)
    with Ds(path, 'r') as d:
        for var_name in var_list:
            var = np.array(d.variables[var_name])
            np.save(os.path.realpath(store_path) + '/' + date + "_"     \
                    + var_name + '.npy', var, allow_pickle=True)


def create_metadata_file(data: str, dest: str, var_list: str):
    pass


def get_var_name_list(path: str) -> [str]:
    list = []
    with Ds(path, 'r') as d:
        for var in d.variables.keys():
            list.append(var)
    return list


def get_date_range(path: str) -> str:
    with Ds(path, 'r') as d:
        return str(d.RangeBeginningDate) + "_" + str(d.RangeEndingDate)


if __name__ == '__main__':
    fire.Fire({
        "single": extract_var_from_file,
        "all": extract_all
    })
