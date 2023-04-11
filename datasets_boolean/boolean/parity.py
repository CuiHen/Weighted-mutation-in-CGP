# !/usr/bin/env python

"""

"""
import numpy as np
from datasets_boolean.dataset_class import Dataset


class Parity(Dataset):
    def __init__(self):
        super().__init__()
        self.x = [[[0, 0, 0], [1]],
                  [[0, 0, 1], [0]],
                  [[0, 1, 0], [0]],
                  [[0, 1, 1], [1]],
                  [[1, 0, 0], [0]],
                  [[1, 0, 1], [1]],
                  [[1, 1, 0], [1]],
                  [[1, 1, 1], [0]], ]
