#!/bin/env python

import matplotlib.pyplot as plt
import netCDF4
import xarray
import numpy
import time


def main():
    concatenate_data()
    #save_to_npy()


# concatenate individual files into one
def concatenate_data():
    # get first time measurement
    tic = time.perf_counter()
    # open all the data sets at once
    data = xarray.open_mfdataset('../.downloads/202008*.nc4', \
                               combine = 'by_coords', concat_dim="time")
    # save the opened files in one file
    data.to_netcdf('../.downloads/combined.nc4')
    data.close()
    # get second time measurement and print result
    toc = time.perf_counter()
    print(f"Concatenated 10.7GB in {toc - tic:0.4f} seconds")


# save *.nc4 to *.npy
def save_to_npy():
    # get first time measurement
    tic = time.perf_counter()
    # load the large file using numpy
    data = numpy.load("../.downloads/combined.nc4")
    numpy.save('../.downloads/data.npy', data)
    # get second time measurement and print result
    toc = time.perf_counter()
    print(f"Saved as .npy in {toc - tic:0.4f} seconds")


# main entry point and function
if __name__ == "__main__":
    main()
