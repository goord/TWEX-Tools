#!/usr/bin/env python

import matplotlib.pyplot as plt
import os
import re
import argparse
import numpy
import netCDF4
import datetime
from dateutil import parser


def plot_prc_hist(ensemble,eifile,date,box):
    eidataset = netCDF4.Dataset(eifile,'r')
    eitimvar = eidataset.variables["time"]
    eitimes = netCDF4.num2date(eitimvar[:],getattr(eitimvar,"units",None))
    eiprecip = eidataset.variables["tp"]
    i = 0
    midpr = 0
    daypr = []
    for t in eitimes:
        if(t.hours == 12): midpr = numpy.mean(eiprecip[i,:,:],axes = [1,2])
        elif(t.hours == 0): daypr.append(midpr + numpy.mean(eiprecip[i,:,:],axes = [1,2]))
        i += 1
    eidataset.close()
    dayptmm = 1000. * numpy.array(daypr)
    plt.hist(dayprmm,20)
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draw precipitation histogram")
    parser.add_argument("--dir" ,dest = "dir", help = "<Required> TWEX ensemble directory",required = True)
    parser.add_argument("--date",dest = "date",help = "Event date (derived from dirname if omitted)",default = None)
    parser.add_argument("--exp", dest = "exp", help = "<Optional> Experiment name",default = "b0if" )
    parser.add_argument("--loc", dest = "loc", nargs = "+",help = "<Required> Data location: either WestCoast, Svalbard a lat-lon pair"
                                                                 "or a lat-lon box (latmin latmax lonmin lonmax)")
    args = parser.parse_args()
    path,exp,loc = args.dir,args.exp,args.loc
    box = utils.getbox(loc)
    date = None
    if(args.date):
        date = parser.parse(args.date)
    else:
        innerdir = os.path.normpath(path).split(os.sep)[-1]
        matches = re.search("(?<=MEM[1-6]_)[0-9]{8}",innerdir)
        if(not matches.group(0)):
            raise Exception("Could not deduce date for directory %s" % innerdir)
        date = parser.parse(matches.group(0))
    eidata = retrieve_prmon(date.month,os.path.join(path,"ei_tp.nc"))
    ensemble = ensoutput.ensemble_store(path,exp)
    plot_prc_hist(ensemble,eidata,date,box)
