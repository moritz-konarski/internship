#!/bin/env python

from netCDF4 import Dataset
import numpy

def main():
    extract_vars('./20191010.nc4', './')
    

def extract_vars(path: str, store_path: str):
    with Dataset(path, 'r') as d:
        for var_name in get_var_name_list(path):
            var = numpy.array(d.variables[var_name])
            numpy.save(store_path + var_name + '.npy', var)


def get_var_name_list(path: str) -> [str]:
    list = []
    with Dataset(path, mode='r') as d:
        for var in d.variables.keys():
            list.append(var)
    return list



if __name__ == '__main__':
    main()
