#!/bin/env python

import xarray


def main():
    concatenate_data('../.year/*.nc4', '../.year/year.nc4')


# concatenate individual files into one
def concatenate_data(path: str, dest: str):
    with xarray.open_mfdataset(path, combine
            = 'by_coords', concat_dim="time") as ds:
        data.to_netcdf(dest)


if __name__ == '__main__':
    main()
