from ecmwfapi import ECMWFDataServer

request = {"stream"  : "oper",
           "levtype" : "sfc",
           "param"   : "228.128",
           "dataset" : "interim",
           "step"    : "0",
           "grid"    : "0.75/0.75",
           "time"    : "00/06/12/18",
           "date"    : None,
           "type"    : "an",
           "class"   : "ei",
           "format"  : "netcdf",
           "target"  : None}

server = ECMWFDataServer()
server.retrieve(request)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create precip histogram")
    parser.add_argument("--path",dest = "path",help = "<Required> Data location",required = True)
    parser.add_argument("--loc",dest = "loc",nargs = "+",help = "<Required> Data location: either WestCoast, Svalbard a lat-lon pair or a lat-lon box (latmin latmax lonmin lonmax)")
    parser.add_argument("--var",dest = "variable",help = "<Required> Variable (mlsp|pr|tas)",required = True)
    args = parser.parse_args()
    path,loc = args.path,args.loc
    box = utils.getbox(loc)

