#!/bin/env python

from netCDF4 import Dataset as Ds
import numpy as np

def main():
    extract_vars('./20191010.nc4', './')
    

def extract_vars(path: str, store_path: str):
    with Ds(path, 'r') as d:
        for var_name in get_var_name_list(path):
            var = np.array(d.variables[var_name])
            np.save(store_path + '_' + var_name + '.npy', var)


def get_var_name_list(path: str) -> [str]:
    list = []
    with Ds(path, mode='r') as d:
        for var in d.variables.keys():
            list.append(var)
    return list


if __name__ == '__main__':
    main()
