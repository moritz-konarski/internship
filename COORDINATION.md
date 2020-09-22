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
- [ ] who does what
    - Akylbek
    - Aidai
    - Moritz
