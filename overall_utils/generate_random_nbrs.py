# !/usr/bin/env python

"""

"""
import numpy as np
import random
from bisect import bisect


def generate_random_number(lower_limit, upper_limit, excluded):
    """

    :param lower_limit:
    :param upper_limit:
    :param excluded:
    :return:
    """
    if lower_limit == upper_limit:
        return lower_limit

    while True:
        random_number = random.randint(lower_limit, upper_limit)
        # if excluded too small,
        if random_number != excluded:
            break

    return random_number


def weighted_choice(values, weights):
    """

    :param values:
    :param weights:
    :return:
    """
    total = 0
    cum_weights = []
    for w in weights:
        total += w
        cum_weights.append(total)
    x = random.random() * total
    i = bisect(cum_weights, x)
    return values[i]


def generate_weighted_random_number(lower_limit, upper_limit, excluded, weights):
    """

    :param lower_limit:
    :param upper_limit:
    :param excluded:
    :param weights:
    :return:
    """
    if lower_limit == upper_limit:
        return lower_limit

    while True:
        # include both lower limit and upper limit. Thus, upper_limit + 1 for choices
        # returns a list. Thus, get the first element of the list as we want a numerical value instaed of a list
        # weights = weights / weights.sum()
        # random_number = np.random.choice(np.arange(lower_limit, upper_limit + 1), p=weights)
        random_number = weighted_choice(np.arange(lower_limit, upper_limit + 1), weights)
        # if excluded too small,
        if random_number != excluded:
            break

    return random_number
