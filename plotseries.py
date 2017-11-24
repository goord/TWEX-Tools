#!/usr/bin/env python

import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator,DateFormatter
import argparse
import numpy
import ensoutput
import datetime
import utils
import ensoutput

def plotseries(ensemble_output,box,pltvars):
    if(not ensemble_output):
        raise Exception("Ensemble output path has not been specified")
    members = ensemble_output.get_members()
    if(len(members) < 1):
        print "No ensemble members found in " + ensemble_output.path
    variables = [v for v in pltvars if v in ensemble_output.get_variables()]
    fig,axes = plt.subplots(3,len(variables))
    for i in range(len(variables)):
        axes[0,i].ticklabel_format(style='sci', axis='y', scilimits=(-2,2))
        axes[1,i].ticklabel_format(style='sci', axis='y', scilimits=(-2,2))
        axes[2,i].ticklabel_format(style='sci', axis='y', scilimits=(-2,2))
        tims = ensemble_output.get_times(variables[i],1)
        valsarr = numpy.zeros([len(members),len(tims)])
        varnotfound = False
        j = 0
        for mem in members:
            vals = ensemble_output.get_timeseries(box,variables[i],mem)
            if(not any(vals)):
                print "Variable",variables[i],"not found in member",mem
                varnotfound = True
                continue
            else:
                varnotfound = False
            axes[0,i].set_title(variables[i])
            if(mem == 0):
                axes[0,i].plot(tims,vals,linewidth = 2,color = "red")
                axes[1,i].plot(tims,vals,linewidth = 2,color = "red")
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
        axes[1,i].plot(tims,mean,"k",linewidth=1)
        stdplus,stdmin = mean + std,mean - std
        axes[1,i].fill_between(tims,stdplus,stdmin,facecolor = 'black',alpha = 0.25)
        stdline, = axes[2,i].plot(tims,std,label = "spread")
        rmseline, = axes[2,i].plot(tims,rmse,label = "rmse")
        axes[2,i].legend(handles = [stdline,rmseline])
        days = DayLocator()
        xformat = DateFormatter("%d-%m")
        evtdate = tims[0] + datetime.timedelta(days = 5)
        for k in [0,1,2]:
            axes[k,i].xaxis.set_major_locator(days)
            axes[k,i].xaxis.set_major_formatter(xformat)
            axes[k,i].axvspan(evtdate,evtdate + datetime.timedelta(days=1),color = "blue",alpha = 0.3)
    fig.autofmt_xdate()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draw ensemble time series")
    parser.add_argument("--path",dest = "path",help = "<Required> Data location",required = True)
    parser.add_argument("--loc", dest = "loc",nargs = "+",help = "<Required> Data location: either WestCoast, Svalbard a lat-lon pair"
                                                                 "or a lat-lon box (latmin latmax lonmin lonmax)")
    parser.add_argument("--vars",dest = "vars",nargs = "+",help = "<Required> Variable list, choose from (%s)" % ensoutput.ensemble_store.get_vars('|'),required = True)
    parser.add_argument("--exp", dest = "exp",help = "<Optional> Experiment name",default = "b0if" )
    args = parser.parse_args()
    path,exp,loc = args.path,args.exp,args.loc
    ensemble = ensoutput.ensemble_store(path,exp)
    box = utils.getbox(loc)
    plotseries(ensemble,box,args.vars)
