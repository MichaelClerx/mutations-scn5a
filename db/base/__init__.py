#!/usr/bin/env python3
#
# SCN5A Mutations DB module
#
#
# Paths
#
import os
import inspect
# Module directory
try:
    frame = inspect.currentframe()
    DIR = os.path.realpath(os.path.dirname(inspect.getfile(frame)))
finally:
    del(frame)
# Cache file
DIR_CACHE = os.path.join(DIR, '_cache')
FILE_CACHE = 'mutations.sqlite'
# Root directory
DIR_ROOT = os.path.abspath(os.path.join(DIR, '..'))
# Data input files
DIR_DATA_IN = os.path.join(DIR_ROOT, 'data-in')
# Data output files
DIR_DATA_OUT = os.path.join(DIR_ROOT, 'data-out')
# Figure input files
DIR_FIGURES_IN = os.path.join(DIR_ROOT, 'figures-in')
# Figure input files
DIR_FIGURES_OUT = os.path.join(DIR_ROOT, 'figures-out')
# Delete imported libraries
del(os, inspect)
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
from ._task import Task, TaskRunner
