from glob2 import glob
import os.path
import netCDF4
import numpy

class ensemble_store(object):

    def __init__(self,path):
        self.path = path
        self.memdirs = {}
        self.latvar,self.lonvar,self.timvar = "lat","lon","time"
        for memdir in glob(os.path.join(path,"member_[0-9]")):
            n = memdir.rindex('_')
            m = int(memdir[n + 1:])
            self.memdirs[m] = memdir
        self.variables = {}

    def get_members(self):
        return self.memdirs.keys()

    def get_variables(self):
        return self.variables.keys()

    def get_dataset(self,varname,member):
        ncfile = self.get_netcdf(varname,self.memdirs[member])
        return netCDF4.Dataset(ncfile,'r')

    def get_netcdf(self,varname,memdir):
        raise Exception("Finding the netcdf file for variable" + varname + "is not implemented in this base class")

    def get_variable(self,varname,member):
        dataset = self.get_dataset(varname,member)
        ncvar = self.variables.get(varname,varname)
        return dataset.variables.get(ncvar,None)

    def get_field(self,timestep,varname,member):
        var = self.get_variable(varname,member)
        if(not var):
            return None
        vardims = len(var.shape)
        if(vardims == 3):
            if(varname == "prcum"):
                return numpy.sum(var[0:timestep+1,:,:],axis = 0)
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
        variable = ds.variables[self.timvar]
        return netCDF4.num2date(variable[:],units = getattr(variable,"units",None),calendar = "gregorian")

    def get_timeseries(self,box,varname,member):
        var = self.get_variable(varname,member)
        if(not var):
            return None
        lats = self.get_lats(varname,member)[:]
        lons = self.get_lons(varname,member)[:]
        if(len(box) == 2):
            lat,lon = box[0],box[1]
            i = numpy.abs(lats - float(lat)).argmin()
            j = numpy.abs(lats - float(lon)).argmin()
            if(varname == "prcum"):
                return numpy.cumsum(var[:,i,j],axis = 0)
            return var[:,i,j]
        if(len(box) == 4):
            latmin,latmax,lonmin,lonmax = box[0],box[1],box[2],box[3]
            i1 = numpy.abs(lats - float(latmin)).argmin()
            i2 = numpy.abs(lats - float(latmax)).argmin()
            imin,imax = min(i1,i2),max(i1,i2)
            j1 = numpy.abs(lons - float(lonmin)).argmin()
            j2 = numpy.abs(lons - float(lonmax)).argmin()
            jmin,jmax = min(j1,j2),max(j1,j2)
            var = self.get_variable(varname,member)
            if(varname == "prcum"):
                return numpy.cumsum(numpy.mean(var[:,imin:imax,jmin:jmax],axis = (1,2)),axis = 0)
            return numpy.mean(var[:,imin:imax,jmin:jmax],axis = (1,2))
        return None


class multinetcdf(ensemble_store):

    def __init__(self,path):
        super(multinetcdf,self).__init__(path)
        self.variables = {"ivt":"ivt","mlsp":"var151","pr":"pr","tas":"var167","prcum":"pr"}

    def get_netcdf(self,varname,memdir):
        ppdir = os.path.abspath(os.path.join(memdir,"postproc"))
        os.path.join(ppdir,varname + ".nc")


class singlenetcdf(ensemble_store):

    def __init__(self,path):
        super(singlenetcdf,self).__init__(path)
        self.variables =
        {"tcw":"TCW","tcwv":"TCWV","mlsp":"MLS","tas":"T2M","uas":"U10M","vas":"V10M","pr":"TP","prcum":"TP"}

    def get_netcdf(self,varname,memdir):
        return os.path.join(memdir,"ICMGGb0if.nc")
