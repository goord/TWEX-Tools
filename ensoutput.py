from glob2 import glob
import os.path
import netCDF4
import numpy

class ensemble_store:

    def __init__(self,path):
        self.path = path
        self.memdirs = {}
        self.latvar,self.lonvar,self.timvar = "lat","lon","time"
        for memdir in glob(os.path.join(path,"member_[0-9]")):
            n = memdir.rindex('_')
            m = int(memdir[n + 1:])
            self.memdirs[m] = memdir
        self.variables = {}

    def get_dataset(self,varname,member):
        ncfile = self.get_netcdf(varname,self.memdirs[member])
        return netCDF4.Dataset(ncfile,'r')

    def get_netcdf(self,varname,memdir):
        raise Exception("Finding the netcdf file for variable" + varname + "is not implemented in this base class")

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

    def get_lats(self,varname,member):
        ds = self.get_dataset(varname,member)
        return ds.variables[self.latvar]

    def get_lons(self,varname,member):
        ds = self.get_dataset(varname,member)
        return ds.variables[self.lonvar]

    def get_times(self,varname,member):
        ds = self.get_dataset(varname,member)
        return ds.variables[self.timvar]

    def get_timeseries(self,lat,lon,varname,member):
        var = self.get_variable(varname,member)
        i = numpy.abs(self.get_lats(varname,member)[:] - float(lat)).argmin()
        j = numpy.abs(self.get_lons(varname,member)[:] - float(lon)).argmin()
        return var[:,i,j]


class multinetcdf(ensemble_store):

    def __init__(self,path):
        super(multinetcdf,self).__init__(path)
        self.variables = {"ivt":"ivt","mlsp":"var151","pr":"pr","tas":"var167"}

    def get_netcdf(self,varname,memdir):
        ppdir = os.path.abspath(os.path.join(memdir,"postproc"))
        os.path.join(ppdir,varname + ".nc")


class singlenetcdf(ensemble_store):

    def __init__(self,path):
        super(multinetcdf,self).__init__(path)
        self.variables = {"tcw":"var136","tcwv":"var137","mlsp":"var151","tas":"var167","uas":"var165","vas":"var166","pr":"var228"}

    def get_netcdf(self,varname,memdir):
        return os.path.join(memdir,"ICMGGb0if.nc")
