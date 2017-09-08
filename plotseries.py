#!/usr/bin/env python

import matplotlib.pyplot as plt
import argparse
import numpy
import ensoutput

def plotseries(ensemble_output,lat,lon):
    if(not ensemble_output):
        raise Exception("Ensemble output path has not been specified")
    if(len(ensemble_output.members) < 1):
        print "No ensemble members found in " + ensemble_output.path
    fields = ensemble_output.fieldids
    fig,axes = plt.subplots(2,len(fields))
    for i in range(len(fields)):
        axes[0,i].ticklabel_format(style='sci', axis='y', scilimits=(-2,2))
        axes[1,i].ticklabel_format(style='sci', axis='y', scilimits=(-2,2))
        fid = fields[i]
        tims = ensemble_output.get_times(fid,1)
        valsarr = numpy.zeros([len(ensemble_output.members),len(tims)])
        for mem in ensemble_output.members:
            vals = ensemble_output.get_timeseries(lat,lon,fid,mem)
            axes[0,i].set_title(fid)
            if(mem == 0):
                axes[0,i].plot(tims,vals,"--k",linewidth=2)
            else:
                axes[0,i].plot(tims,vals)
            valsarr[mem,:] = vals[:]
        mean = numpy.mean(valsarr[1:,:],0)
        std = numpy.std(valsarr,0)
        rmse = numpy.sqrt(numpy.mean((valsarr[1:,:]-valsarr[0,:])**2,0))
        axes[0,i].plot(tims,mean,"k",linewidth=1)
        stdline, = axes[1,i].plot(tims,std,label = "spread")
        rmseline, = axes[1,i].plot(tims,rmse,label = "rmse")
        axes[1,i].legend(handles = [stdline,rmseline])
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draw ensemble time series")
    parser.add_argument("--path",dest = "path",help = "<Required> Data location",required = True)
    parser.add_argument("--lat",dest = "lat",help = "<Required> Point latitude",required = True)
    parser.add_argument("--lon",dest = "lon",help = "<Required> Point longitude",required = True)
    parser.add_argument("--mul",dest = "ncstore",action = "store_const",const = "multi",default = "single" )
    args = parser.parse_args()
    path,lat,lon = args.path,args.lat,args.lon
    ensemble = None
    if(args.ncstore == "single"):
        ensemble = ensoutput.singlenetcdf(path)
    elif(args.ncstore == "multi"):
        ensemble = ensoutput.multinetcdf(path)
    plotseries(ensemble,lat,lon)
