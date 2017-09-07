from glob2 import glob
import os.path
import netCDF4
import numpy

class ensemble_store:

    def __init__(self,path):
        self.path = path
        self.memdirs = {}
        self.variables = {}
        for memdir in glob(os.path.join(path,"member_[0-9]")):
            n = memdir.rindex('_')
            m = int(memdir[n + 1:])
            self.memdirs[m] = memdir

    def get_dataset(self,varname,member):
        ncfile = self.get_netcdf(varname,self.memdirs[member])
        return netCDF4.Dataset(ncfile,'r')

    def get_variable(self,varname,member):
        dataset = self.get_dataset(varname,member)
        ncvar = self.variables.get(varname,varname)
        return dataset.variables[ncvar]

    def get_field(self,timestep,varname,member):
        var = get_variable(self,varname,member)
        vardims = len(var.shape)
        if(vardims == 3):
            return var[timestep,:,:]
        raise Exception("Variables of shape " + var.shape + "are not supported")


class ensoutput:

    fieldids = ["ivt","mlsp","pr","tas"]
    ncvars = {"ivt":"ivt","mlsp":"var151","pr":"pr","tas":"var167"}
    members = []

    def __init__(self,path):
        self.path = path
        memdirs = glob(os.path.join(path,"member_*"))
        self.ncpaths = {}
        for memdir in memdirs:
            n = memdir.rindex('_')
            m = int(memdir[n + 1:])
            self.members.append(m)
            ppdir = os.path.abspath(os.path.join(memdir,"postproc"))
            for fid in self.fieldids:
                ncpath = os.path.join(ppdir,fid + ".nc")
                if(os.path.isfile(ncpath)):
                    self.ncpaths[(m,fid)] = ncpath
                else:
                    print "Warning: file " + ncpath + " does not exist"

    def validate_memindex(self,i):
        if(i not in self.members):
            raise Exception("Ensemble member index " + str(i) + " out of range")

    def get_dataset(self,fieldid,member):
        self.validate_memindex(member)
        if(fieldid not in self.fieldids):
            raise Exception("Field id " + fieldid + " is not supported")
        if((member,fieldid) not in self.ncpaths):
            raise Exception("Member " + str(member) + " does not contain data for " + fieldid)
        ncfile = self.ncpaths[(member,fieldid)]
        return netCDF4.Dataset(ncfile,'r')

    def get_variable(self,fieldid,member):
        ds = self.get_dataset(fieldid,member)
        var = ds.variables.get(self.ncvars[fieldid],None)
        if(not var):
            raise Exception("Netcdf file does not contain variable " + self.ncvars[fieldid])
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
        lons = ds.variables.get("lon",None)
        return lons[:]

    def get_times(self,fieldid,member):
        ds = self.get_dataset(fieldid,member)
        tims = ds.variables.get("time",None)
        return tims[:]

    def get_timeseries(self,lat,lon,fieldid,member):
        var = self.get_variable(fieldid,member)
        i = numpy.abs(self.get_lats(fieldid,member) - float(lat)).argmin()
        j = numpy.abs(self.get_lons(fieldid,member) - float(lon)).argmin()
        return var[:,i,j]


class ecmwf_ensemble(ensoutput):

    fieldids = ["tcw","tcwv","mlsp","tas","uas","vas","pr"]
    ncvars = {"tcw":"var136","tcwv":"var137","mlsp":"var151","tas":"var167","uas":"var165","vas":"var166","pr":"var228"}

    def __init__(self,path):
        self.path = path
        memdirs = glob(os.path.join(path,"member_*"))
        self.ncpaths = {}
        for memdir in memdirs:
            n = memdir.rindex('_')
            m = int(memdir[n + 1:])
            ncpath = os.path.join(memdir,"ICMGGb0if.nc")
            if(os.path.isfile(ncpath)):
            	self.ncpaths[m] = ncpath
            	self.members.append(m)
            else:
                print "Warning: file " + ncpath + " does not exist"

    def validate_memindex(self,i):
        if(i not in self.ncpaths):
            raise Exception("Ensemble member index " + str(i) + " out of range")

    def get_dataset(self,fieldid,member):
        self.validate_memindex(member)
        if(fieldid not in self.ncvars):
            raise Exception("Field id " + fieldid + " is not supported")
        ncfile = self.ncpaths[member]
        return netCDF4.Dataset(ncfile,'r')

    def get_variable(self,fieldid,member):
        ds = self.get_dataset(fieldid,member)
        var = ds.variables.get(self.ncvars[fieldid],None)
        if(not var):
            raise Exception("Netcdf file does not contain variable " + self.ncvars[fieldid])
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
        lons = ds.variables.get("lon",None)
        return lons[:]

    def get_times(self,fieldid,member):
        ds = self.get_dataset(fieldid,member)
        tims = ds.variables.get("time",None)
        return tims[:]

    def get_timeseries(self,lat,lon,fieldid,member):
        var = self.get_variable(fieldid,member)
        i = numpy.abs(self.get_lats(fieldid,member) - float(lat)).argmin()
        j = numpy.abs(self.get_lons(fieldid,member) - float(lon)).argmin()
        return var[:,i,j]
