# Extractor

- should take input of variables that are desired
- should take list or dir of files to process
- concatenate all into their respective \*.npy files
- each deconstructed netCDF file gets a json file
- then all the individual vars are named after `date_varname.npy`

- store metadata in a json file for each variable
    - number of dimensions and their names
    - time that is covered, units, names
    - resolution
    - where the data comes from

- what type of metadata is needed?
    - json
    - synthesize these files -- create a directory each time a netcdf file is
    extracted -- makes it simpler to manage, then open the dir with my function
    and it reads the into file
    - variables and their units
    - start and end time
    - frequency of measurements -- times of measurements
    - dimension of variables
    - 
