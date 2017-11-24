#!/usr/bin/env python

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import os
import argparse
import numpy
import heapq
import netCDF4
import datetime
import calendar
from dateutil import parser
import ensoutput
import utils

def get_extremes(files,nmaxes,varname):
    result = []
    for f in files:
        print "Reading file...",f
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
        arr = 1000. * var[:].flatten()
        if(var.shape[0] != len(timestamps)):
            print "Variable %s is not a 1D time series in file %f... skipping file" % (varname,f)
            continue
        for i in range(len(timestamps)):
            yr = timestamps[i].year
            if(yr in valsbyyear):
                valsbyyear[yr].append(arr[i])
            else:
                valsbyyear[yr] = [arr[i]]
        for yr in valsbyyear:
            if(len(valsbyyear[yr]) != (366 if calendar.isleap(yr) else 365)): continue
            print "File %s, year %d: %d largest values are %s" % (f,yr,nmaxes,str(heapq.nlargest(nmaxes,valsbyyear[yr])))
            result.extend(heapq.nlargest(nmaxes,valsbyyear[yr]))
        ds.close()
        print "...ok"
    print result
    return result

def gumbel(x,mu,beta):
    return (1/beta)*numpy.exp(-(x-mu)/beta)*numpy.exp(-numpy.exp(-(x-mu)/beta))

def gumbel_cdf(x,mu,beta):
    return numpy.exp(-numpy.exp(-(x-mu)/beta))

def plotgumbel(data,nbins,ensemble = None):
    plt.style.use("ggplot")
    variance = numpy.var(data)
    mean = numpy.mean(data)
    beta = numpy.sqrt(6*variance)/numpy.pi
    mu = mean - 0.57721*beta
    count,bins,ignored = plt.hist(data,nbins,color = "grey",label = "FW Present")
    norm = numpy.sum(count*(bins[1]-bins[0]))
    finebins = numpy.linspace(bins[0],bins[-1],1000)
    plt.plot(finebins,norm*gumbel(finebins,mu,beta),linewidth=1.5,color="black")
    ensdata = []
    if(ensemble):
        memprmm = []
        for m in ensemble.get_members():
            times = ensemble.get_times("pr",m)
            middle_time = times[0] + (times[-1] - times[0])/2
            series = ensemble.get_timeseries(utils.boxes["westcoast"],"pr",m)
            pr,i = 0.,0
            for time in times:
                if(time.day == middle_time.day):
                    pr += (1000. * series[i])
                i += 1
            memprmm.append(pr)
        count,bins,ignored = plt.hist(memprmm,nbins,color='r',label = "M3 2002-10-18 ens.")
        ensdata = numpy.array(memprmm)
        mean,sigma = numpy.mean(ensdata),numpy.std(ensdata)
        x = numpy.linspace(mean - 3* sigma,mean + 3*sigma)
        norm = numpy.sum(count*(bins[1]-bins[0]))
        plt.plot(x,norm*mlab.normpdf(x,mean,sigma),linewidth=1.5,color='purple')
    plt.xlabel("yearly max. 24h precipitation [mm]")
    plt.legend()
    plt.show()
    if(ensemble):
        data = numpy.append(data,ensdata)
    ranks = len(data) + 1 - numpy.argsort(numpy.argsort(numpy.array(data)))
    a = 0.44
    T = (len(data) + 1.00 -2*a)/(ranks - a)
    origsize = len(data) - len(ensdata)
    plt.scatter(T[0:origsize],data[0:origsize],marker = 'o',color = 'grey',label = "FW Present")
    plt.scatter(T[origsize:],data[origsize:],marker = 'o',color = 'r',label = "M3 2002-10-18 ens.")
    sorteddata = numpy.sort(data[0:origsize])[::-1]
    plt.plot(1./(1. - gumbel_cdf(sorteddata,mu,beta)),sorteddata,linewidth = 2.0,color = "black")
    plt.ylabel("yearly max. 24h precipitation [mm]")
    plt.xlabel("return time (yr)")
    plt.gca().set_xscale("log")
    plt.gca().set_xlim(left = numpy.min(T))
    plt.gca().set_ylim(bottom = numpy.min(data))
    plt.legend()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot yearly extremes histogram of netcdf timeseries files")
    parser.add_argument(dest = "files", type = str, nargs='+', help = "<Required> Input Netcdf time series files")
    parser.add_argument("--var",dest = "var", help = "<Required> Variable name",required = True)
    parser.add_argument("--nmax",dest = "nmax",type = int,default = 1,help = "number of max events per year")
    parser.add_argument("--bins",dest = "nbins",type = int,default = 10,help = "number of histogram bins")
    parser.add_argument("--extr",dest = "extrpath",type = str,default = None,help = "extra ensemble path")
    args = parser.parse_args()
    files,varname,nummaxes,nbins = args.files,args.var,args.nmax,args.nbins
    data = get_extremes(files,nummaxes,varname)
    ensemble = None
    if(args.extrpath):
        ensemble = ensoutput.ensemble_store(args.extrpath,"b0if")
    plotgumbel(data,nbins,ensemble)
