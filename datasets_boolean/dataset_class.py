# !/usr/bin/env python

"""

"""
import numpy as np


class Dataset:
    def __init__(self):
        self.x = None

    def __call__(self):
        data = []
        label = []

        for d, l in self.x:
            data.append(d)
            label.append(l)

        return np.array(data, dtype=np.bool), np.array(label, dtype=np.bool)
