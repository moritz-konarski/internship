# Educational Internship 2020

Internship program at [AUCA](https://auca.kg) and 
[RAS RS](http://www.gdirc.kg/en/) 2020.

## Tasks

### Educational Internship

1) Learn how to use online resources to access NASA earth remote sensing data
2) Familiarization with the netCDF data format for scientific data storage
3) Use libraries to work with nerCDF files in different computing environments

### Industrial Internship

1) Registration on NASA Earthdata platform to access satellite data
2) Development of a library for working with NetCDF satellite data in Python 
3) Development of a computer application visualizing NASA MERRA2 satellite 
reanalysis data

## TODO List

### General 

- [ ] update README
- [ ] translate exercises to be sure what I am expected to do

### Downloader 

- [ ] write proper wrapper for wget in python
- [ ] remove link printing from downloader, add 'x or total' info
- [ ] add basic completion checking using filenames

### File Management

#### Convert netCDF to NPY

- [ ] write proper converter that takes input of list of files or file with
names
- [ ] use \*.csv or \*.json to store metadata for the data
- [ ] __use \*.npy format for data storage__
- [ ] finally zipping of the data

#### Access Program

- [ ] coordinate with others about precise abilities of our functions
- [ ] create templates for data retrieval for plotting
    - [ ] get var list () -> [str]
    - [ ] get var type
    - [ ] get var unit
    - [ ] get coordinate range (var) [lat\_min, lat\_max, lon\_min, lon\_max]
    - [ ] get time range (var)
    - [ ] get time series (start\_time, end\_time, var, area=[], lev?)
    - [ ] get heat map (time, area, var, lev?)
    - get all data within certain constraints: greater than, smaller than ...

### Additional

- [ ] to be more scientific, we should implement some better analysis features:
    - statistics
    - spectral analysis
    - other time series analysis tools
