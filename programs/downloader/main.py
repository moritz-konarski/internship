#!/usr/bin/python3
"""File Download Helper

This script takes a file of download urls from
https://disc.gsfc.nasa.gov/datasets/M2I3NPASM_5.12.4/summary?keywords=M2I3NPASM_5.12.4
and downloads each of the included files successively.

The url file is the provided text file (.txt) from the website.

The destination folder is a valid directory (name/) where the files will be
stored. The will be saved named after the last full word in their download url.
"""

import requests
from tqdm import tqdm
import re
import os
import sys
import fire


# parses the provided url file into individual file names and download links
def parse_url_file(file: str) -> [(str, str)]:
    """
    Parses a url file, turning it into a list of tuples of (filename, url)
    :param file: the input file containing download urls, one per line
    :return: list of tuples of (filename, url)
    """
    # initialize lists
    url_list = []
    with open(file, 'r') as f:
        for line in f.readlines():
            # remove the whitespace
            stripped_line = line.strip()
            # find the last word and the file extension for the file name
            # e.g. extract '20200703.nc4' from the link
            # https://goldsmr5.gesdisc.eosdis.nasa.gov/data/MERRA2/M2I3NPASM.5.12.4/2020/07/MERRA2_400.inst3_3d_asm_Np.20200703.nc4
            x = re.search(r"[^./_]+\....$", stripped_line)
            # add a tuple of file name and url to the list
            url_list.append((x.group(), stripped_line))
    return url_list


# function to download a file using the provided response and store it
# in the destination folder under filename
def download(filename: str, dest_folder: str, response: requests.request):
    """
    Downloads the file from the url in response, puts it into dest_folder under
    filename
    :param filename: name of the downloaded file
    :param dest_folder: folder to put the file in
    :param response: the response from https requests based on url
    :return:
    """
    # get url from response
    url = response.url
    print('Downloading ' + filename + '\nFrom: ' + url)
    # get total file size
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    # 1 Kibibyte
    block_size = 1024
    # create the progress bar
    with tqdm(total=total_size_in_bytes, unit='iB',
              unit_scale=True) as progress_bar:
        with open(dest_folder + filename, 'wb') as file:
            # for each of the download chunks
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        # check for obvious errors
        if total_size_in_bytes != 0 and \
                progress_bar.n != total_size_in_bytes:
            print("ERROR, something went wrong")
    print('Content written to ' + dest_folder + filename + '\n')


# function to download all the data specified by urls in urlfile, putting it
# into dest_folder
def download_all(url_file: str, dest_folder: str):
    """
    Downloads each of the elements in url_file and saves them to
    dest_folder
    :param url_file: file of download urls from
    https://disc.gsfc.nasa.gov/datasets/M2I3NPASM_5.12.4/summary?keywords=M2I3NPASM_5.12.4
    :param dest_folder: path to the folder where the downloaded files
    should be stored
    :return:
    """

    # exit if the destination folder is not a proper directory name
    if not re.findall(r"/$", dest_folder):
        print("Error: please enter a valid directory name (ending in '/')")
        exit(1)

    # if the folder does not exist, create it
    if not os.path.exists(dest_folder):
        os.mkdir(dest_folder)

    # create the url list from the provided file
    url_list = parse_url_file(url_file)

    try:
        # iterate through the urls and filenames
        for (filename, url) in url_list:
            # get https response for url
            response = requests.get(url, stream=True)
            response.raise_for_status()
            # download associated file
            download(filename, dest_folder, response)
        print("Finished!")
    except requests.exceptions.HTTPError as http_err:
        print("Request Error: ", http_err.args[0])
    except KeyboardInterrupt as kbi:
        print('\nInterrupted -- Aborting Script')
        try:
            sys.exit(1)
        except SystemExit as se:
            sys.exit(se)
    except Exception:
        raise


if __name__ == '__main__':
    # use fire module to do command line interface handling
    fire.Fire({
        "download": download_all
    })
