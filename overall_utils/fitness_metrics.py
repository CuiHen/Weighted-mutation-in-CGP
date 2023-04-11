# !/usr/bin/env python

"""

"""
import numpy as np


def fitness_boolean(model_output, target):
    nbr_correct = np.logical_not(np.logical_xor(model_output, target))
    nbr_correct = np.sum(nbr_correct)

    return 1 - (nbr_correct / model_output.size)


