#!/bin/env python

import os
import fire
import numpy as np
from pathlib import Path

def concat(name: str, path: str, dest: str):
    with open(dest, 'wb') as f:
        for part in Path(path).glob("*" + name + ".npy"):
            filepath = os.path.join(part)
            print(filepath)
            dataArray = np.load(filepath, allow_pickle=True)
            np.save(f, dataArray)


if __name__ == '__main__':
    concat('PS', './files/', './files/PS.npy')
    concat('H', './files/', './files/H.npy')
    concat('O3', './files/', './files/O3.npy')
    concat('EPV', './files/', './files/EPV.npy')

