#!/usr/bin/env python

import matplotlib.pyplot as plt
import os
import argparse
import numpy
import netCDF4

def get_time_variable(ds):
    return ds.variables.get("time",None)

def get_prc_variable(ds):
    return ds.variables.get("prc",None)

def get_prc(path,date):
    files = [f for f in map(os.path.listdir(path),lambda p : os.path.join(path,p)) if os.path.isfile(f)]
    ncfiles = [f for f in files if os.path.splitext(f)[1] == ".nc"]
    prcyr = {}
    for ncf in ncfiles:
        ds = netCDF4.Dataset(ncf,'r')
        timvar = get_time_variable(ds)
        if(not timvar):
            print "Could not detect time variable in file",ncf
            continue
        indices = []
        for i in range(len(timvar)):
            if(timvar[i].month,timvar[i].day == date.month,date.day): indices.append((i,timvar[i].year))
        if(not any(indices)):
            print "Could not find date",date.month,"-",date.day,"in time axis for file",ncfile
        prcvar = get_prc_variable(ds)
        prctot = {}
        for k,v in indices:
            if(k in prctot):
                prctot[k] += prcvar[v]
            else:
                prctot[k] = prcvar[v]
        for k,v in prctot:
            if(k in prcyr):
                prcyr[k].append(v)
            else:
                prcyr[k] = [v]
    return prcyr

def plot_prc_hist(prcyr):
    vals = []
    for k,v in prcyr:
        vals.extend(v)
    plt.hist(vals,20)

if __name__ == "main":
    parser = argparse.ArgumentParser(description="Draw precipitation histogram")
    parser.add_argument("--path",dest = "path",help = "<Required> Data directory",required = True)
    parser.add_argument("--date",dest = "date",help = "<Required> Histogram date (month,day)",required = True)
#    parser.add_argument("--box",dest = "box",nargs = '+',type = float,help = "<Optional> bounding box: latmin lonmin latmax lonmax")
    args = parser.parse_args()
    path = args.path
    date = args.date
#    box = getattr(args,"box",None)
#    boxdict = None if box == None else {}
#    if(len(box) > 0): boxdict["latmin"] = box[0]
#    if(len(box) > 1): boxdict["lonmin"] = box[1]
#    if(len(box) > 2): boxdict["latmax"] = box[2]
#    if(len(box) > 3): boxdict["lonmax"] = box[3]
    data = get_prc(path)
    plot_prc_hist(data)
