#!/usr/bin/env python

import matplotlib.pyplot as plt
import os
import re
import glob
import argparse
import numpy
import heapq
import netCDF4
import datetime
from dateutil import parser

def get_extremes(files,nmaxes,varname):
    result = []
    for f in files:
        valsbyyear = {}
        ds = netCDF4.Dataset(f,'r')
        time = ds.variables.get("Time",None)
        if(not time): time = ds.variables.get("time",None)
        if(not time):
            print "Cannot find time variable in %s...skipping file" % f
            continue
        var = ds.variables.get(varname,None)
        if(not var):
            print "Cannot find %s variable in %s...skipping file" % (varname,f)
            continue
        timeunit = getattr(time,"units",None)
        if(not timeunit):
            print "Cannot find time unit in %s...skipping file" % f
            continue
        timestamps = netCDF4.num2date(time[:],timeunit)
        if(var.shape != (len(timestamps),)):
            print "Variable %s is not a 1D time series in file %f... skipping file" % (varname,f)
            continue
        for i in range(len(timestamps)):
            yr = timestamps[i].year
            if(yr in valsbyyear):
                valsbyyear[yr].append(var[i])
            else:
                valsbyyear[yr] = [var[i]]
        for yr in valsbyyear:
            result.extend(heapq.nlargest(nmaxes,valsbyyear[yr]))
    ds.close()
    return result

def gumbel(x,mu,beta):
    return (1/beta)*numpy.exp(-(x-mu)/beta)*numpy.exp(-numpy.exp(-(x-mu)/beta))

def gumbel_cdf(x,mu,beta):
    return numpy.exp(-numpy.exp(-(x-mu)/beta))

def plotgumbel(data,nbins):
    plt.style.use("ggplot")
    variance = numpy.var(data)
    mean = numpy.mean(data)
    beta = numpy.sqrt(6*variance)/numpy.pi
    mu = mean - 0.57721*beta
    count,bins,ignored = plt.hist(data,nbins,normed = True,color = 'grey')
    bins = numpy.linspace(bins[0],bins[-1],1000)
    plt.plot(bins,gumbel(bins,mu,beta),linewidth=2,color='r')
    plt.xlabel("yearly max. 24h precipitation [mm]")
    plt.show()
    ranks = len(data) + 1 - numpy.argsort(numpy.argsort(numpy.array(data)))
    a = 0.44
    T = (len(data) + 1.00 -2*a)/(ranks - a)
    plt.scatter(T,data,marker = 'o')
    sorteddata = numpy.sort(data)[::-1]
    plt.plot(1./(1. - gumbel_cdf(sorteddata,mu,beta)),sorteddata,linewidth = 2.0)
    plt.ylabel("yearly max. 24h precipitation [mm]")
    plt.xlabel("return time")
    plt.gca().set_xscale("log")
    plt.gca().set_xlim(left = numpy.min(T))
    plt.gca().set_ylim(bottom = numpy.min(data))
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot yearly extremes histogram of netcdf timeseries files")
    parser.add_argument(dest = "data", help = "<Required> Input Netcdf time series files")
    parser.add_argument("--var",dest = "var", help = "<Required> Variable name",required = True)
    parser.add_argument("--nmax",dest = "nmax",type = int,default = 1,help = "number of max events per year")
    parser.add_argument("--bins",dest = "nbins",type = int,default = 10,help = "number of histogram bins")
    args = parser.parse_args()
    datapath,varname,nummaxes,nbins = args.data,args.var,args.nmax,args.nbins
    files = [ f for f in glob.glob(datapath) if len(os.path.splitext(f)) == 2 and os.path.splitext(f)[1] == ".nc" ]
    data = get_extremes(files,nummaxes,varname)
    plotgumbel(data,nbins)
