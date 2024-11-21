#!/usr/bin/env python3
#
# SCN5A Mutations DB module
#


# Paths
import os
import inspect
try:
    frame = inspect.currentframe()
    DIR = os.path.realpath(os.path.dirname(inspect.getfile(frame)))
finally:
    del inspect, frame


# Cache file
DIR_CACHE = os.path.join(DIR, '_cache')
if not os.path.exists(DIR_CACHE):
    os.makedirs(DIR_CACHE)
FILE_CACHE = 'midpoints.sqlite'

# Root directory
DIR_ROOT = os.path.abspath(os.path.join(DIR, '..'))

# Data input files
DIR_DATA_IN = os.path.join(DIR_ROOT, 'data-in')
del os

# CSV File options
CSV_OPTIONS = {
    'delimiter' : ',',
    'quotechar' : '"',
    'skipinitialspace' : True,
    }

#
# Import functions and classes
#
from ._connection import connect

