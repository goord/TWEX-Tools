#!/usr/bin/env python

import matplotlib.pyplot as plt
import argparse
import numpy
from ensoutput import ensoutput

ensemble_output = None

def initialize(path):
    global ensemble_output
    ensemble_output = ensoutput(path)

def plotseries(lat,lon):
    if(not ensemble_output):
        raise Exception("Ensemble output path has not been specified")
    if(ensemble_output.memcount < 1):
        print "No ensemble members found in " + ensemble_output.path
    nvars = len(ensemble_output.fieldids)
    fig,axes = plt.subplots(nvars)
    i = 0
    for fid in ensemble_output.fieldids:
        tims = ensemble_output.get_times(fid,1)
        for mem in range(1,ensemble_output.memcount + 1):
            vals = ensemble_output.get_timeseries(lat,lon,fid,mem)
            axes[i].set_title(fid)
            axes[i].plot(tims,vals)
        i += 1
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draw ensemble maps")
    parser.add_argument("path")
    parser.add_argument("lat")
    parser.add_argument("lon")
    args = parser.parse_args()
    path = args.path
    lat = getattr(args,"lat",0)
    lon = getattr(args,"lon",0)
    initialize(path)
    plotseries(lat,lon)
