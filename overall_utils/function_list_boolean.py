# !/usr/bin/env python

"""

"""
import numpy as np


class Functions:
    def __init__(self):
        super().__init__()
        self.function_dict = {
            0: self.AND,
            1: self.OR,
            2: self.NAND,
            3: self.NOR,
        }

        self.nbr_params_dict = {
            0: 2,
            1: 2,
            2: 2,
            3: 2,
        }

    def __len__(self):
        return len(self.function_dict)

    def AND(self, connection0, connection1):
        return np.logical_and(connection0, connection1)

    def OR(self, connection0, connection1):
        return np.logical_or(connection0, connection1)

    def NAND(self, connection0, connection1):
        return np.logical_not(np.logical_and(connection0, connection1))

    def NOR(self, connection0, connection1):
        return np.logical_not(np.logical_or(connection0, connection1))


