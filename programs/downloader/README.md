# NetCDF Downloader

A short Python script that downloads files from the specified urls. This script
is designed to work with urls and NetCDF files from
<https://disc.gsfc.nasa.gov/datasets/M2I3NPASM_5.12.4/summary?keywords=M2I3NPASM_5.12.4>

## Requirements and Setup

1. Go to <https://disc.gsfc.nasa.gov/data-access> and follow steps 1, 2, and
3 to create a Earthdata account and link it to GES DISC.
2. Follow steps 1 and 2 outlined in
<https://disc.gsfc.nasa.gov/data-access#python-requests> to get setup for this
script.
1. install [anaconda](https://www.anaconda.com/) for environment management (or
use something equivalent).
2. clone this git repository and navigate to this folder
```bash 
git clone https://github.com/moritz-konarski/internship.git
```
3. create a conda environment from the included `downloader.yml` file by 
running
```bash
conda env create --file downloader.yml
```

## Basic Usage

1. Start the conda environment in this directory
```bash
conda activate downloader
```
2. Run the script with
```bash
python3 main.py
```
3. Deactivate the conda environment with
```bash
conda deactivate
```

## Practical Example

1. Start the conda environment.
2. To download data from a text file containing links called `urls.txt` and 
store them in a directory called `downloads/` in the same folder, run
```bash
python3 main.py download urls.txt downloads/
```
The files will be saved under the last word in their url plus their file
extension, e.g.
`https://goldsmr5.gesdisc.eosdis.nasa.gov/data/MERRA2/M2I3NPASM.5.12.4/2020/07/MERRA2_400.inst3_3d_asm_Np.20200703.nc4`
will be turned into `20200703.nc4`

__Take note that NetCDF files can be large (> 1GB) so it might take a while for
them to download__
3. Deactivate the environment when you are done.
