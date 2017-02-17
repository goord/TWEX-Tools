#!/usr/bin/env python

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import argparse
import numpy
from ensoutput import ensoutput

ensemble_output = None

def initialize(path):
    global ensemble_output
    ensemble_output = ensoutput(path)

def plotfield(fieldid,timeindex,boundingbox = None):
    if(not ensemble_output):
        raise Exception("Ensemble output path has not been specified")
    if(ensemble_output.memcount < 1):
        print "No ensemble members found in " + ensemble_output.path
    lats = ensemble_output.get_lats(fieldid,1)
    lons = ensemble_output.get_lons(fieldid,1)
    lons,lats = numpy.meshgrid(lons,lats)
    fig,axes = plt.subplots(3,ensemble_output.memcount/3)
    mem = 0
    for axis in axes.flat:
        mem += 1
        axis.set_title(fid + " member " + str(mem))
        m = Basemap(lon_0 = 0,resolution = 'h',ax = axis)
        data = ensemble_output.get_field(timeindex,fieldid,mem)
        im1 = m.pcolormesh(lons,lats,data,shading='flat',cmap=plt.cm.jet,latlon=True)
        cb = m.colorbar(im1,"bottom", size="5%", pad="2%")
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draw ensemble maps")
    parser.add_argument("path")
    parser.add_argument("variable")
    parser.add_argument("timeindex")
    args = parser.parse_args()
    path = args.path
    fid = args.variable
    time = args.timeindex
    initialize(path)
    plotfield(fid,time)
