#!/usr/bin/env python

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import argparse
import numpy
import ensoutput

ensemble_output = None

def initialize(path):
    global ensemble_output
    ensemble_output = ensoutput.singlenetcdf(path)

def plotfield(fieldid,timeindex,boundingbox = None,member = 0):
    if(not ensemble_output):
        raise Exception("Ensemble output path has not been specified")
    if(member not in ensemble_output.get_members()):
        print "Member " + str(member) +" not found in " + str(ensemble_output.get_members())
        return
    lats = ensemble_output.get_lats(fieldid,1)
    lons = ensemble_output.get_lons(fieldid,1)
    lons,lats = numpy.meshgrid(lons,lats)
    plt.title(fid + " member " + str(member))
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
        m = Basemap(resolution = 'h',llcrnrlon = lonmin,
                    llcrnrlat = latmin,urcrnrlon = lonmax,urcrnrlat = latmax,
                    projection = "merc")
    data = ensemble_output.get_field(timeindex,fieldid,member)
    m.contour(lons,lats,data,linewidths = 0.5,colors = 'k',latlon = True)
    im1 = m.contourf(lons,lats,data,20,cmap = plt.cm.jet,latlon = True,)
    m.drawcoastlines()
    cb = m.colorbar(im1)
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draw ensemble maps")
    parser.add_argument("--path",dest = "path",help = "<Required> Data location",required = True)
    parser.add_argument("--var",dest = "variable",help = "<Required> Variable (ivt|mlsp|pr|tas)",required = True)
    parser.add_argument("--mem",dest = "member",help = "<Required> Member (0-9)",required = True)
    parser.add_argument("--tim",dest = "timeindex",help = "<Required> Time index",required = True)
    parser.add_argument("--box",dest = "box",nargs = '+',type = float,help = "<Optional> bounding box: latmin lonmin latmax lonmax")
    args = parser.parse_args()
    path = args.path
    fid = args.variable
    time = args.timeindex
    mem = int(args.member)
    box = getattr(args,"box",None)
    boxargs = 0 if box == None else len(box)
    boxdict = {}
    if(boxargs > 0): boxdict["latmin"] = box[0]
    if(boxargs > 1): boxdict["lonmin"] = box[1]
    if(boxargs > 2): boxdict["latmax"] = box[2]
    if(boxargs > 3): boxdict["lonmax"] = box[3]
    initialize(path)
    plotfield(fid,time,boxdict,mem)
