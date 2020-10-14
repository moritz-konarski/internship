# Meeting 14-10-2020

## TODO

- [x] make 4D data somehow plottable
    - for a heat map we freeze time, have controls to choose the time and date, 
    range of lats and lons, 
    - time series: lock lat and lon -- have control over position, start, end
    - potentially make a heat map that is 3D, draw contour lines
    - save the results in different format -- png, pdf, etc; for time series
    make option to download as .csv or .dat
    - use pandas data frames after importing the data??
    - use series structure from pandas -- makes it simple to slice this data
    type
    - statistical calculation also in pandas
    - load npz, work as dataframe, save using .to_txt(), .to_csv(), etc.
    - 
- gui:
    - menu bar for tabs for the different elements, open file, save file, help,
    save as (pdf, png, csv...)
    - toolbox bar
    - one of the frames that has a plot
    - control box
    - status bar on main window -- loading.., plotting.., loaded file x
    - even if there is little functionality, have the stuff there for practice
- [ ] write proper docs of the data manager
- [ ] unify plotter to one class
- [ ] make a data class that does the handling of data requests?
- [ ] make json reader in plotter
- [ ] plot heat maps and time series according to requirements
- [ ] use metadata to create plots
- next meeting is next week on Wednesday at 15:00
