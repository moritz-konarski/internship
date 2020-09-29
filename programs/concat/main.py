#!/bin/env python

import fire
import numpy as np
from pathlib import Path

def concat(name: str, path:str):
    with open(path, 'wb'):
        for part in Path(path).glob("*" + varname + ".npy"):
            # Find the path of the file
            filepath = os.path.join(path, npfile)
            print filepath
            # Load file
            dataArray= np.load(filepath)
            print dataArray
            np.save(f_handle,dataArray)
    dataArray= np.load(fpath)
    print dataArray







if __name__ == '__main__':

