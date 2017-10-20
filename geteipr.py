from ecmwfapi import ECMWFDataServer
import datetime
import os

def retrieve_data(date,datadir):
    eifile = os.path.join(datadir,"ei_pr.nc")
    month = date.strftime("%B")
    if(not os.path.isfile(eifile)):
        request = {"stream"  : "oper",
                   "levtype" : "sfc",
                   "param"   : "228.128",
                   "dataset" : "interim",
                   "step"    : "3/6/9/12",
                   "grid"    : "N400",
                   "time"    : "00/06/12/18",
                   "date"    : month,
                   "type"    : "an",
                   "class"   : "ei",
                   "format"  : "netcdf",
                   "target"  : eifile}
        print "The request is",request
        server = ECMWFDataServer()
        server.retrieve(request)
    return eifile


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create precip histogram")
    parser.add_argument("--path",dest = "path",help = "<Required> Data location",required = True)
    parser.add_argument("--loc",dest = "loc",nargs = "+",help = "<Required> Data location: either WestCoast, Svalbard a lat-lon pair or a lat-lon box (latmin latmax lonmin lonmax)")
    args = parser.parse_args()
    path,loc = args.path,args.loc
    box = utils.getbox(loc)
