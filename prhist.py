#!/usr/bin/env python

import matplotlib.pyplot as plt
import os
import argparse
import numpy
import netCDF4
import datetime


def get_time_variable(ds):
    for k,v in ds.variables.iteritems():
        if(k == "time" or v.standard_name == "time"):
            return v
    return None


def get_prc_variable(ds):
    return ds.variables.get("pr",None)


def get_index_box(ds,latlonbox):
    latvar,lonvar = None,None
    for k,v in ds.variables.iteritems():
        if(k == "lat" or getattr(v,"standard_name",None) == "latitude"):
            latvar = v
        if(k == "lon" or getattr(v,"standard_name",None) == "longitude"):
            lonvar = v
    if(not (latvar and lonvar)):
        print "Variables latitude and longitude not found in dataset"
        return {}
    latmin = getattr(latlonbox,"latmin",None)
    latmax = getattr(latlonbox,"latmax",None)
    lonmin = getattr(latlonbox,"lonmin",None)
    lonmax = getattr(latlonbox,"lonmax",None)
    imin = numpy.abs(lonvar[:]-lonmin).argmin() if lonmin else 0
    imax = numpy.abs(lonvar[:]-lonmax).argmin() if lonmax else (len(lonvar[:])-1)
    jmin = numpy.abs(latvar[:]-latmin).argmin() if latmin else 0
    jmax = numpy.abs(latvar[:]-latmax).argmin() if latmax else (len(latvar[:])-1)
    return {"imin":imin,"imax":imax,"jmin":jmin,"jmax":jmax}


def get_prc_day(path,month,day,latlonbox):
    files = [f for f in map(lambda p : os.path.join(path,p),os.listdir(path)) if os.path.isfile(f)]
    ncfiles = [f for f in files if os.path.splitext(f)[1] == ".nc"]
    prctot = []
    for ncf in ncfiles:
        print "Reading file",ncf,"..."
        ds = netCDF4.Dataset(ncf,'r')
        timvar = get_time_variable(ds)
        if(not timvar):
            print "Could not detect time variable in file",ncf
            continue
        times = netCDF4.num2date(timvar[:],units=timvar.units,calendar=timvar.calendar)
        indices = {}
        for i in range(len(timvar)):
            if(times[i].month == month and (day <= 0 or times[i].day == day)):
                y,d = times[i].year,times[i].day
                if((y,d) in indices): indices[(y,d)].append(i)
                else: indices[(y,d)] = [i]
        if(not any(indices)):
            print "Could not find date",month,"-",(day if day > 0 else "*"),"in time axis for file",ncf
            continue
        print "Number of timestamps:",len(indices)
        indexbox = get_index_box(ds,latlonbox)
        prcvar = get_prc_variable(ds)
        for (k,v) in indices.iteritems():
            prtot = 0.
            for i in v:
                prtot += numpy.mean(prcvar[i,indexbox["jmin"]:indexbox["jmax"],indexbox["imin"]:indexbox["imax"]])
            date = datetime.date(year=k[0],month = month,day = k[1])
            prctot.append((date,1000*prtot))
    return prctot


def plot_prc_hist(vals):
    plt.hist([v[1] for v in vals],20)
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draw precipitation histogram")
    parser.add_argument("--path",dest = "path",help = "<Required> Data directory",required = True)
    parser.add_argument("--month",dest = "month",help = "<Required> Histogram month",required = True)
    parser.add_argument("--day",dest = "day",help = "<Optional> Histogram day")
    parser.add_argument("--box",dest = "box",nargs = '+',type = float,help = "<Optional> bounding box: latmin lonmin latmax lonmax")
    args = parser.parse_args()
    path = args.path
    month = int(args.month)
    daystr = getattr(args,"day")
    day = int(daystr) if daystr else 0
    box = getattr(args,"box",None)
    boxdict = None if box == None else {}
    boxargs = 0 if box == None else len(box)
    if(boxargs > 0): boxdict["latmin"] = box[0]
    if(boxargs > 1): boxdict["lonmin"] = box[1]
    if(boxargs > 2): boxdict["latmax"] = box[2]
    if(boxargs > 3): boxdict["lonmax"] = box[3]
    data = get_prc_day(path,month,day,boxdict)
    print "Number of collected data points:",len(data)
    plot_prc_hist(data)
