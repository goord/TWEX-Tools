#!/usr/bin/env python

import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator,DateFormatter
import argparse
import numpy
import ensoutput
import datetime
import utils

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
    parser.add_argument("--loc", dest = "loc",nargs = "+",help = "<Required> Data location: either WestCoast, Svalbard a lat-lon pair"
                                                                 "or a lat-lon box (latmin latmax lonmin lonmax)")
    parser.add_argument("--var", dest = "var",help = "<Required> Variable (%s)" % ensoutput.ensemble_store.get_vars('|'),required = True)
    parser.add_argument("--exp", dest = "exp",help = "<Optional> Experiment name",default = "b0if" )
    args = parser.parse_args()
    path,exp,loc = args.path,args.exp,args.loc
    ensemble = ensoutput.ensemble_store(path,exp)
    box = utils.getbox(loc)
    plotplume(ensemble,box,args.var)
