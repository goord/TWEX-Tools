#!/usr/bin/env python

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import os
import re
import argparse
import numpy
import netCDF4
import datetime
from dateutil import parser as dateparser
from geteipr import retrieve_prmon
import utils
import ensoutput


def plot_prc_hist(ensemble,eifile,date,box):
    plt.style.use("ggplot")
    eidataset = netCDF4.Dataset(eifile,'r')
    eitimvar = eidataset.variables["time"]
    eitimes = netCDF4.num2date(eitimvar[:],getattr(eitimvar,"units",None))
    eiprecip = eidataset.variables["tp"]
    i = 0
    midpr = 0
    daypr = []
    for t in eitimes:
        if(t.hour == 12): midpr = numpy.mean(eiprecip[i,:,:],axis = (0,1))
        elif(t.hour == 0): daypr.append(midpr + numpy.mean(eiprecip[i,:,:],axis = (0,1)))
        i += 1
    eidataset.close()
    dayprmm = 1000. * numpy.array(daypr)
    memprmm = []
    bins = numpy.linspace(0,100,40)
    plt.hist(dayprmm,bins,normed = True,color='b',label = "Era-Interim")
    for m in ensemble.get_members():
        times = ensemble.get_times("pr",m)
        series = ensemble.get_timeseries(box,"pr",m)
        pr,i = 0.,0
        for time in times:
            if(time.day == date.day):
                print "adding pr at",time,"to total:",series[i]
                pr += (1000. * series[i])
            i += 1
        print "Total precip member",m,"is",pr
        memprmm.append(pr)
    plt.hist(memprmm,bins,normed = True,color='r',label = "Future extreme event")
    prarray = numpy.array(memprmm)
    mu,sigma = numpy.mean(prarray),numpy.std(prarray)
    x = numpy.linspace(mu - 3* sigma,mu + 3*sigma)
    plt.plot(x,mlab.normpdf(x,mu,sigma),linewidth=1.5,linestyle = ":",color='r')
    plt.legend()
    plt.xlabel("Daily precip [mm]")
    plt.title("Daily precip October west coast region")
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
        date = dateparser.parse(args.date)
    else:
        innerdir = os.path.normpath(path).split(os.sep)[-1]
        matches = re.search("(?<=MEM[1-6]_)[0-9]{8}",innerdir)
        if(not matches or not matches.group(0)):
            raise Exception("Could not deduce date for directory %s" % innerdir)
        date = dateparser.parse(matches.group(0))
    eidata = retrieve_prmon(date.month,os.path.join(path,"ei_tp.nc"),box)
    ensemble = ensoutput.ensemble_store(path,exp)
    plot_prc_hist(ensemble,eidata,date,box)
