#!/usr/bin/python3
# This is a test script to experiment with downloading files using Python.

import requests
from tqdm import tqdm
import re
import os
import fire


# parses the provided url file into individual file names and download links
def parse_url_file(file: str) -> [(str, str)]:
    url_list = []
    with open(file, 'r') as f:
        for line in f.readlines():
            stripped_line = line.strip()
            x = re.search(r"[^.]+\....$", stripped_line)
            url_list.append((x.group(), stripped_line))
    return url_list


def download(url_file: str, dest_folder: str):
    """
    Downloads each of the elements in url_file and saves them to
    dest_folder
    :param url_file: file of download urls from
    https://disc.gsfc.nasa.gov/datasets/M2I3NPASM_5.12.4/summary?keywords=M2I3NPASM_5.12.4
    :param dest_folder: path to the folder where the downloaded files
    should be stored
    :return:
    """
    if not os.path.exists(dest_folder):
        os.mkdir(dest_folder)

    url_list = parse_url_file(url_file)

    try:
        for (filename, url) in url_list:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            # print downloading information
            print('Downloading ' + filename + '\nFrom: ' + url)

            # get https response
            total_size_in_bytes = int(response.headers.get('content-length', 0))
            # 1 Kibibyte
            block_size = 1024
            progress_bar = tqdm(total=total_size_in_bytes, unit='iB',
                                unit_scale=True)
            with open(dest_folder + filename, 'wb') as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
            progress_bar.close()
            if total_size_in_bytes != 0 and \
                    progress_bar.n != total_size_in_bytes:
                print("ERROR, something went wrong")
            print('Content written to ' + dest_folder + filename + '\n')
    except requests.exceptions:
        print(
            'requests.get() returned an error code ' + str(
                response.status_code))


if __name__ == '__main__':
    fire.Fire({
        "download": download
    })
