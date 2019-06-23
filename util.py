"""
    util.py
    A small collection of useful functions

    Given an homogenous list, returns the items of that list concatenated together.
"""
from functools import reduce


def collapse(data):
    return reduce(lambda x, y: x + y, data)


""" Given a string and a number n, cuts the string up, returns a
    list of strings, all size n. 
"""


def slice(string, n):
    temp = []
    i = n
    while i <= len(string):
        temp.append(string[(i-n):i])
        i += n

    # Add on any stragglers
    try:
        if string[(i-n)] != "":
            temp.append(string[(i-n):])
    except IndexError:
        pass

    return temp
