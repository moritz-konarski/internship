#!/bin/env python

import os
import fire
import numpy as np
from pathlib import Path

# TODO: make sure that only the files that have dates are used here
# it should not try to load itself in the process
def concat(name: str, path: str, dest: str):
    with open(dest, 'wb') as f:
        for part in Path(path).glob("*" + name + ".npz"):
            filepath = os.path.join(part)
            print(filepath)
            dataArray = np.load(filepath, allow_pickle=True)
            #print(dataArray['arr_0'])
            np.savez_compressed(f, dataArray['arr_0'], allow_pickle=True)


if __name__ == '__main__':
    concat('_PS', './test/', './test/PS.npz')
    concat('_H', './test/', './test/H.npz')
    concat('_O3', './test/', './test/O3.npz')
    concat('_EPV', './test/', './test/EPV.npz')

