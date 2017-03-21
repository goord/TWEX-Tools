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
    if(len(ensemble_output.members) < 1):
        print "No ensemble members found in " + ensemble_output.path
    lats = ensemble_output.get_lats(fieldid,1)
    lons = ensemble_output.get_lons(fieldid,1)
    lons,lats = numpy.meshgrid(lons,lats)
    fig,axes = plt.subplots(3,(len(ensemble_output.members)+2)/3)
    i = 0
    for axis in axes.flat:
        if(i == len(ensemble_output.members)): break
        mem = ensemble_output.members[i]
        i += 1
        axis.set_title(fid + " member " + str(mem))
        if(not boundingbox):
            m = Basemap(lon_0 = 0,resolution = 'h',ax = axis)
        else:
            boxdict = None
            if(isinstance(boundingbox,dict)):
                boxdict = boundingbox
            else:
                boxdict = boundingbox.__dict__
            lonmin = boxdict.get("lonmin",-180.)
            latmin = boxdict.get("latmin",-90.)
            lonmax = boxdict.get("lonmax",180.)
            latmax = boxdict.get("latmax",90.)
            m = Basemap(resolution = 'h',ax = axis,llcrnrlon = lonmin,
                        llcrnrlat = latmin,urcrnrlon = lonmax, urcrnrlat = latmax, projection = "merc")
        data = ensemble_output.get_field(timeindex,fieldid,mem)
#        im1 = m.pcolormesh(lons,lats,data,shading = 'flat',cmap = plt.cm.jet,latlon = True)
        m.contour(lons,lats,data,linewidths = 0.5,colors = 'k',latlon = True)
        im1 = m.contourf(lons,lats,data,cmap = plt.cm.jet,latlon = True)
        m.drawcoastlines()
        cb = m.colorbar(im1)
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draw ensemble maps")
    parser.add_argument("--path",dest = "path",help = "<Required> Data location",required = True)
    parser.add_argument("--var",dest = "variable",help = "<Required> Variable (ivt|mlsp|pr|tas)",required = True)
    parser.add_argument("--tim",dest = "timeindex",help = "<Required> Time index",required = True)
    parser.add_argument("--box",dest = "box",nargs = '+',type = float,help = "<Optional> bounding box: latmin lonmin latmax lonmax")
    args = parser.parse_args()
    path = args.path
    fid = args.variable
    time = args.timeindex
    box = getattr(args,"box",None)
    boxdict = None if box == None else {}
    if(len(box) > 0): boxdict["latmin"] = box[0]
    if(len(box) > 1): boxdict["lonmin"] = box[1]
    if(len(box) > 2): boxdict["latmax"] = box[2]
    if(len(box) > 3): boxdict["lonmax"] = box[3]
    initialize(path)
    plotfield(fid,time,boxdict)
