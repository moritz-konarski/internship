# Coordination

## 22.09.2020

- Github to host code
- Conda as main environment

## Discussion for 23.09.

- [ ] splitting into individual variable files
    - only feasible if we only work with a few variables
    - otherwise takes up more space (6.3 MB vs 5.8 MB)
    - probably because lat, lon, lev, time are copied each time
- [ ] main parts of the project
    - wget downloader using python
        - download status
        - take url files as input
        - put files in specified directory
        - maybe automatic download url file creation with NASA website
    - file manager
        - splitting of files
        - isolating variables
        - concatenating files
    - plotter
        - color, scale, area, var range control
        - heat map
        - time series
    - GUI
        - selector menus
        - calenders for date selection
- [ ] who does what and who downloads which part of the year (4 months
sections, they have data until August 2020)
    - Akylbek -- 
    - Aidai   -- 
    - Moritz  -- 
- PyQt5 seems good

- 3 main sections
    1. download + file management   -- Moritz 
        - download class:
            - url file input
            - download initiation
            - download status
            - download progress
            - download folder setting
        - management class:
            - splitting into files?
            - returning slices for plotting -- heat maps, time series
            - deleting files?
            - deleting unwanted variables
    2. plotting                     -- Aidai 
        - plan
    3. GUI                          -- Akylbek
        - plan
- make plan on a call -- we'll talk about the organization at 3pm
- make a rough plan

## Coordination Meeting

- what each of us will do:
    - Moritz : will download and manage data -- provide the data to Aidai so
    she can just plot
    - Aidai  : will create visualizations
    - Akylbek: will create the GUI
- data structure:
    - we can't delete variables beforehand because we don't know
    - we should use a different data structure to store and access data
    - use a type of database to store that information -- no
- separate them into files.
- databases: <https://www.unidata.ucar.edu/blogs/developer/en/entry/netcdf_schema_language>
- convert netCDF into files with extracted time stamps -- converts it to better
data structure -- provide the tools to Aidai to do that stuff
- good data structure for the data
- convert nc4 -> good structure -> selector for time period and 
