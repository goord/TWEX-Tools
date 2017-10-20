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

def plotfield(fieldid,timeindex,boundingbox = None):
    if(not ensemble_output):
        raise Exception("Ensemble output path has not been specified")
    if(len(ensemble_output.get_members()) < 1):
        print "No ensemble members found in " + ensemble_output.path
    lats = ensemble_output.get_lats(fieldid,1)
    lons = ensemble_output.get_lons(fieldid,1)
    lons,lats = numpy.meshgrid(lons,lats)
    fig,axes = plt.subplots(3,(len(ensemble_output.get_members())+2)/3)
    i = 0
    for axis in axes.flat:
        if(i == len(ensemble_output.get_members())): break
        axis.set_title(fid + " member " + str(i))
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
                        llcrnrlat = latmin,urcrnrlon = lonmax,urcrnrlat = latmax,
                        projection = "merc")
        data = ensemble_output.get_field(timeindex,fieldid,i)
        m.contour(lons,lats,data,linewidths = 0.5,colors = 'k',latlon = True)
        im1 = m.contourf(lons,lats,data,cmap = plt.cm.jet,latlon = True)
        m.drawcoastlines()
        cb = m.colorbar(im1)
        i += 1
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draw ensemble maps")
    parser.add_argument("--path",dest = "path",help = "<Required> Data location",required = True)
    parser.add_argument("--var",dest = "variable",help = "<Required> Variable (%s)" % ensoutput.ensemble_store.get_vars('|'),required = True)
    parser.add_argument("--tim",dest = "timestep",help = "<Required> Time step",default = 0)
    parser.add_argument("--box",dest = "box",nargs = '+',type = float,help = "<Optional> bounding box: latmin lonmin latmax lonmax")
    args = parser.parse_args()
    path = args.path
    fid = args.variable
    time = args.timestep
    box = getattr(args,"box",None)
    boxargs = 0 if box == None else len(box)
    boxdict = {}
    if(boxargs > 0): boxdict["latmin"] = box[0]
    if(boxargs > 1): boxdict["lonmin"] = box[1]
    if(boxargs > 2): boxdict["latmax"] = box[2]
    if(boxargs > 3): boxdict["lonmax"] = box[3]
    initialize(path)
    plotfield(fid,time,boxdict)
