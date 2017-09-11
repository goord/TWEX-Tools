#!/usr/bin/env python

import matplotlib.pyplot as plt
import argparse
import numpy
import ensoutput

def plotseries(ensemble_output,box,pltvars):
    if(not ensemble_output):
        raise Exception("Ensemble output path has not been specified")
    members = ensemble_output.get_members()
    if(len(members) < 1):
        print "No ensemble members found in " + ensemble_output.path
    variables = [v for v in pltvars if v in ensemble_output.get_variables()]
    fig,axes = plt.subplots(2,len(variables))
    for i in range(len(variables)):
        axes[0,i].ticklabel_format(style='sci', axis='y', scilimits=(-2,2))
        axes[1,i].ticklabel_format(style='sci', axis='y', scilimits=(-2,2))
        tims = ensemble_output.get_times(variables[i],1)
        valsarr = numpy.zeros([len(members),len(tims)])
        varnotfound = False
        j = 0
        for mem in members:
            vals = ensemble_output.get_timeseries(box,variables[i],mem)
            if(vals == None):
                print "Variable",variables[i],"not found in member",mem
                varnotfound = True
                continue
            else:
                varnotfound = False
            axes[0,i].set_title(variables[i])
            if(mem == 0):
                axes[0,i].plot(tims,vals,linewidth = 2,color = "red")
            valsarr[j,:] = vals[:]
            j += 1
        if varnotfound: continue
        maxline = numpy.amax(valsarr,axis = 0)
        minline = numpy.amin(valsarr,axis = 0)
        axes[0,i].fill_between(tims,minline,maxline,facecolor = 'red',alpha = 0.5)
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
    parser.add_argument("--lat",dest = "lat",nargs = "+",help = "<Required> Latitude range (or value)",required = True)
    parser.add_argument("--lon",dest = "lon",nargs = "+",help = "<Required> Longitude range (or value)",required = True)
    parser.add_argument("--mul",dest = "ncstore",action = "store_const",const = "multi",default = "single" )
    parser.add_argument("--vars",dest = "vars",nargs = "+",help = "Plot variable list",required = True)
    args = parser.parse_args()
    path,lat,lon = args.path,args.lat,args.lon
    box = None
    if(len(lat) == 1 and len(lon) == 1):
        box = [lat[0],lon[0]]
    elif(len(lat) == 2 and len(lon) == 2):
        box = [lat[0],lat[1],lon[0],lon[1]]
    else:
        raise Exception("Unsupported combination of latitudes " + str(lat) + " and longitudes " + str(lon))
    ensemble = None
    if(args.ncstore == "single"):
        ensemble = ensoutput.singlenetcdf(path)
    elif(args.ncstore == "multi"):
        ensemble = ensoutput.multinetcdf(path)
    plotseries(ensemble,box,args.vars)
