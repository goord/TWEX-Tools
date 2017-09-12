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
    parser.add_argument("--loc",dest = "loc",nargs = "+",help = "<Required> Data location: either WestCoast, Svalbard a lat-lon pair or a lat-lon box (latmin latmax lonmin lonmax)")
    parser.add_argument("--mul",dest = "ncstore",action = "store_const",const = "multi",default = "single" )
    parser.add_argument("--vars",dest = "vars",nargs = "+",help = "Plot variable list",required = True)
    args = parser.parse_args()
    path,loc = args.path,args.loc
    box = None
    if(len(loc) == 1):
        locstring = str(loc[0]).lower()
        if(locstring == "westcoast"):
            box = [59.616826,61.474623,4.836320,7.560929]
        elif(locstring == "svalbard"):
            box = [77.778678,79.228149,13.909666,18.686065]
    elif(len(loc) == 2):
        box = [float(loc[0]),float(loc[1])]
    elif(len(loc) == 4):
        box = [float(loc[0]),float(loc[1]),float(loc[2]),float(loc[3])]
    else:
        raise Exception("Unsupported location specification " + str(loc))
    ensemble = None
    if(args.ncstore == "single"):
        ensemble = ensoutput.singlenetcdf(path)
    elif(args.ncstore == "multi"):
        ensemble = ensoutput.multinetcdf(path)
    plotseries(ensemble,box,args.vars)
