# This is a test script to experiment with downloading files using Python.

import os
from subprocess import run

link = "https://acdisc.gesdisc.eosdis.nasa.gov/data/" \
       "/Aqua_AIRS_Level3/" \
       "AIRX3STD.006/2006/" \
       "AIRS.2006.12.31.L3.RetStd001.v6.0.9.0.G13155192744.hdf"

link2 = "https://hydro1.gesdisc.eosdis.nasa.gov/data/GLDAS/GLDAS_NOAH025_3H.2.0/2014/365/GLDAS_NOAH025_3H.A20141231.0000.020.nc4"

path = "/home/moritz/Documents/internship.git/programs/download_helper/downloads"


def create_download_script(url: str, destination_folder: str,
                           recursively: bool) -> [str]:
    return ["wget",
            "--load-cookies", "/home/moritz/.urs_cookies",
            "--save-cookies", "/home/moritz/.urs_cookies",
            "--auth-no-challenge=on",
            "--keep-session-cookies",
            "--content-disposition",
            url,
            "-P",
            destination_folder,
            "-np"]
    # TODO add recursive and directory functionality


# TODO: create a progress bar or read the output and display it
# --no-verbose


if __name__ == '__main__':
    script = create_download_script(link2, path)
    output = run(script, text=True, check=True)
    print("hello")
    print(output)
