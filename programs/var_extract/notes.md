# Extractor

- should take input of variables that are desired
- should take list or dir of files to process
- concatenate all into their respective \*.npy files
- store metadata in a json file for each variable
    - number of dimensions and their names
    - time that is covered, units, names
    - resolution
    - where the data comes from
- each deconstructed netCDF file gets a json file
- then all the individual vars are named after `date_varname.npy`
