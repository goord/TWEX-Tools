import os
import calendar
import ecmwfapi
import utils

def retrieve_prmon(mon,eifile,box = None):
    dx = 1.25
    if(not os.path.isfile(eifile)):
        request = {"stream"  : "oper",
                   "levtype" : "sfc",
                   "param"   : "228.128",
                   "dataset" : "interim",
                   "step"    : "3/6/9/12",
                   "grid"    : '/'.join([str(dx),str(dx)]),
                   "time"    : "00/06/12/18",
                   "date"    : calendar.month_name[mon],
                   "type"    : "an",
                   "class"   : "ei",
                   "format"  : "netcdf",
                   "target"  : eifile
                   }
        if(box):
            extent = []
            if(len(box) == 1):
                extent = [box[0] + dx,box[1] - dx,box[0] - dx,box[1] + dx]
            else:
                extent = [box[2],box[1],box[0],box[3]]
            request["area"] = '/'.join([str(c) for c in extent])
        print "The request is",request
        server = ecmwfapi.ECMWFDataServer()
        server.retrieve(request)
    return eifile


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve era-interim precipitation data")
    parser.add_argument("--path",dest = "path",help = "<Required> Target location",required = True)
    parser.add_argument("--loc",dest = "loc",nargs = "+",help = "<Required> Data location: either WestCoast, Svalbard or "
                                                                "a lat-lon pair or a lat-lon box (latmin latmax lonmin lonmax)")
    parser.add_argument("--mon",dest = mon,help = "<Required> Month 1-12",required = True)
    args = parser.parse_args()
    path,loc,mon = args.path,getattr(args,"loc",None),args.mon
    box = utils.getbox(loc) if loc else None
    retrieve_prmon(mon,path,box)
