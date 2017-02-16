from glob2 import glob
import os.path
import netCDF4

class ensoutput:

    fieldids = ["ivt","msl","pr"]

    def __init__(self,path):
        memdirs = glob(os.path.join(path,"member_*"))
        self.memcount = len(memdirs)
        self.ncpaths = {}
        i = 0
        for memdir in memdirs:
            i += 1
            ppdir = os.path.abspath(os.path.join(memdir,"postproc"))
            for fid in self.ncpaths:
                ncpath = os.path.join(ppdir,fid + ".nc")
                if(os.path.isfile(ncpath)):
                    self.ncpaths[(i,fid)] = ncpath
                else:
                    print "Warning: file " + ncpath + " does not exist"

    def validate_memindex(self,i):
        if(i < 1 || i > self.memcount):
            raise Exception("Ensemble member index out of range")

    def get_dataset(self,fieldid,member):
        self.validate_memindex(member)
        if(fieldid not in fieldids):
            raise Exception("Field id " + fieldid + " is not supported")
        if((member,fieldid) not in self.ncpaths):
            raise Exception("Member " + str(member) + "does not contain data for " + fieldid)
        ncfile = self.ncfiles[(member,fieldid)]
        return netCDF4.Dataset(ncfile,'r')

    def get_variable(self,fieldid,member):
        ds = self.get_dataset(fieldid,member)
        var = ds.variables.get(fieldid,None)
        if(not var):
            raise Exception("Netcdf file " + ncfile + " does not contain variable " + fieldid)
        return var

    def get_field(self,timestep,fieldid,member):
        var = self.get_variable(fieldid,member)
        return var[timestep,:,:]

    def get_lats(self,fieldid,member):
        ds = self.get_dataset(fieldid,member)
        lats = ds.variables.get("lat",None)
        return lats[:]

    def get_lons(self,fieldid,member):
        ds = self.get_dataset(fieldid,member)
        lats = ds.variables.get("lon",None)
        return lons[:]

    def get_timeseries(lat,lon,fieldid,member):
        var = self.get_variable(fieldid,member)
        i = numpy.abs(self.get_lats(fieldid,member) - lat)
        j = numpy.abs(self.get_lons(fieldid,member) - lon)
        return var[:,i,j]
