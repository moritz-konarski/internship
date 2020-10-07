#!/bin/env python

import os
import re
import sys
import fire
import numpy as np
from pathlib import Path
from netCDF4 import Dataset


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

def extract_var(str_src_path: str, str_dest_path: str, var_name: str):
    """
    Extracts one variable from the specified file and saves it 
    """
    src_path = check_src_path(str_src_path)
    dest_path = check_dest_path(str_dest_path)
    
    # TODO: come up with a good variable name check in this setting
    if var_exists(var_name):
        pass

    if not re.findall(r"/$", store_path):
        store_path + "/"
    if not os.path.exists(store_path):
        os.mkdir(store_path)
    with Ds(path, 'r') as d:
        var = np.array(d.variables[var_name])
        np.save(os.path.realpath(store_path) + '/' + var_name + '.npy', var,
                allow_pickle=True)


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


def get_var_name_list(path: str) -> [str]:
    """
    List all variables in the specified file.
    """
    list = []
    with Dataset(path, 'r') as d:
        for var in d.variables.keys():
            list.append(var)
    return list

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


def print_all_vars(path: str):
    for var in get_var_name_list(path):
        print(var)



def get_date_range(path: str) -> str:
    with Ds(path, 'r') as d:
        return str(d.RangeBeginningDate) + "_" + str(d.RangeEndingDate)



#if __name__ == '__main__':
#    fire.Fire({
#        "single": extract_var_from_file,
#        "all": extract_all
#    })

if __name__ == '__main__':
    #check_src_path('../var_extract')
    #check_dest_path('lol')
    #check_dest_path('hi')
    fire.Fire({
        "list": print_all_vars
    })

    #concat('_PS', './test/', './test/PS.npz')
    #concat('_H', './test/', './test/H.npz')
    #concat('_O3', './test/', './test/O3.npz')
    #concat('_EPV', './test/', './test/EPV.npz')

#!/bin/env python


