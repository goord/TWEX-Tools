#!/usr/bin/env python

import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator,DateFormatter
import argparse
import numpy
import ensoutput
import datetime

plotstyles = {"mlsp":{"color":"red","units":"hPa","longname":"mean sea-level pressure"},
              "tas":{"color":"orange","units":"K","longname":"2m temperature"},
              "prcum":{"color":"blue","units":"m","longname":"precipitation"}}

def plotplume(ensemble_output,box,pltvar):
    plt.style.use("ggplot")
    if(not ensemble_output):
        raise Exception("Ensemble output path has not been specified")
    members = ensemble_output.get_members()
    if(len(members) < 1):
        print "No ensemble members found in " + ensemble_output.path
        return
    if(pltvar not in ensemble_output.get_variables()):
        print "Variable " + pltvar + " not found in " + ensemble_output.get_variables()
        return
    color = plotstyles.get(pltvar,{}).get("color","red")
    units = plotstyles.get(pltvar,{}).get("units","")
    longname = plotstyles.get(pltvar,{}).get("longname",pltvar)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(-2,2))
    tims = ensemble_output.get_times(pltvar,1)
    valsarr = numpy.zeros([len(members),len(tims)])
    j = 0
    for mem in members:
        vals = ensemble_output.get_timeseries(box,pltvar,mem)
        if(vals == None):
            print "Variable",variables[i],"not found in member",mem
            return
        if(mem == 0):
            plt.plot(tims,vals,linewidth = 2.5,color = color)
        else:
            plt.plot(tims,vals,linewidth = 1,linestyle = "-",color = color)
        valsarr[j,:] = vals[:]
        j += 1
    #maxline = numpy.amax(valsarr,axis = 0)
    #minline = numpy.amin(valsarr,axis = 0)
    mean = numpy.mean(valsarr[1:,:],0)
    std = numpy.std(valsarr,0)
    plt.plot(tims,mean,"k",linewidth=1)
    plt.fill_between(tims,mean + std,mean - std,facecolor = color,alpha = 0.3)
    plt.fill_between(tims,mean + 2*std,mean - 2*std,facecolor = color,alpha = 0.1)
    days = DayLocator()
    xformat = DateFormatter("%d-%m")
    plt.gca().xaxis.set_major_locator(days)
    plt.gca().xaxis.set_major_formatter(xformat)
    plt.ylabel(pltvar + "["+ units + "]")
    plt.title(longname)
    plt.gcf().autofmt_xdate()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draw ensemble time series")
    parser.add_argument("--path",dest = "path",help = "<Required> Data location",required = True)
    parser.add_argument("--loc",dest = "loc",nargs = "+",help = "<Required> Data location: either WestCoast, Svalbard a lat-lon pair or a lat-lon box (latmin latmax lonmin lonmax)")
    parser.add_argument("--mul",dest = "ncstore",action = "store_const",const = "multi",default = "single" )
    parser.add_argument("--var",dest = "var",help = "Plot variable",required = True)
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
    plotplume(ensemble,box,args.var)
