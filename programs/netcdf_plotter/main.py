# This is a sample Python script.
# inspired by https://joehamman.com/2013/10/12/plotting-netCDF-data-with-Python/
# https://www2.atmos.umd.edu/~cmartin/python/examples/netcdf_example1.html

from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

my_example_nc_file = '../.downloads/20200701.nc4'

if __name__ == '__main__':
    with Dataset(my_example_nc_file, mode='r') as data:
        print(data.variables)
        # exit(0)
        lons: [float] = data.variables['lon'][:]
        lats: [float] = data.variables['lat'][:]
        T = data.variables['PS'][:, :, :]
        T: [float, float, float] = T[0, :, :]

        lons_1 = []
        print("setting lon")
        for x in lons:
            if 40 < x < 50:
                lons_1.append(x)

        print("setting lats")
        lats_1 = []
        for x in lats:
            if 40 < x < 50:
                lats_1.append(x)

        print("setting T")
        T_1: [float, float, float] = []
        for x as lat in T:
            for lat as
                if 40 < x[1] < 50 and 40 < x[2] < 50:
                    T_1.append(t, x[1], x[2])

        # Set the figure size, projection, and extent
        fig = plt.figure(figsize=(10, 6))
        ax = plt.axes(projection=ccrs.Robinson())
        ax.set_global()
        ax.coastlines(resolution="110m", linewidth=1)
        ax.gridlines(linestyle='--', color='black')

        # Set contour levels, then draw the plot and a colorbar
        clevs = np.arange(75000, 103366, 500)
        plt.contourf(lons_1, lats_1, T_1, clevs, transform=ccrs.PlateCarree(),
                     cmap=plt.cm.jet)
        plt.title('Surface Pressure at 12am 01.07.2020', size=14)
        cb = plt.colorbar(ax=ax, orientation="vertical", pad=0.02, aspect=16,
                          shrink=0.8)
        cb.set_label('Pa', size=12, rotation=0, labelpad=15)
        cb.ax.tick_params(labelsize=10)

        # Save the plot as a PNG image

        fig.savefig('MERRA2_t2m.png', format='png', dpi=400)
