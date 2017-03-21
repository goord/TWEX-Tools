#!/usr/bin/env python

import matplotlib.pyplot as plt
import os
import argparse
import numpy
import netCDF4

def get_nc_series(path,date):
    files = [f for f in map(os.path.listdir(path),lambda p : os.path.join(path,p)) if os.path.isfile(f)]
    monstr = "{:02d}".format(date.month)
    files = [f for f in files if f[-5:] == monstr + ".nc"]
    #TODO: finish
