# `wget` wrapper for netCDF downloads

## Urls 

Urls can be retrieved from 
<https://disc.gsfc.nasa.gov/datasets/M2I3NPASM_5.12.4/summary> by specifying the
desired restricions. This internship works with OPeNDAP and the region 
`65, 34, 83, 48`

## Requirements and Setup

1. Go to <https://disc.gsfc.nasa.gov/data-access> and follow steps 1, 2, and
3 to create an Earthdata account and link it to GES DISC.
2. Follow the steps outlined in
<https://disc.gsfc.nasa.gov/data-access#mac_linux_wget> to get setup for this
script.
3. Install [anaconda](https://www.anaconda.com/) for environment management 
4. Clone this git repository and navigate to this folder
```bash 
git clone https://github.com/moritz-konarski/internship.git
```
5. Create a conda environment from the included `wget_wrapper.yml` file by 
running
```bash
conda env create --file downloader.yml
```

## Basic Usage

1. Start the conda environment in this directory
```bash
conda activate wget_wrapper
```
2. Run the script with
```bash
python3 download.py
```
3. Deactivate the conda environment with
```bash
conda deactivate
```

## Practical Example

1. Get a list of download urls from
[here](https://disc.gsfc.nasa.gov/datasets/M2I3NPASM_5.12.4/summary)
by clicking "Subset / Get Data" in the "Data Access" section, selecting the 
desired data range, and downloading the resulting text file. Save it in this
programs folder.
2. Start the conda environment.
3. To download data from a text file containing links called `urls.txt` and 
store them in a directory called `downloads` in the same folder, run
```bash
python3 download.py from urls.txt downloads
```
5. Deactivate the environment when you are done.
