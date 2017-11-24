from glob2 import glob
import os.path
import netCDF4
import numpy

class ensemble_store(object):

    variables = {"tcw":"TCW","tcwv":"TCWV","mlsp":"MSL","tas":"T2M","uas":"U10M","vas":"V10M","pr":"TP","prcum":"TP"}
    codes = {"tcw":136,"tcwv":137,"mlsp":151,"tas":167,"uas":165,"vas":166,"pr":228,"prcum":228}

    @staticmethod
    def get_vars(delimiter = ','):
        return delimiter.join(ensemble_store.variables.keys())

    def __init__(self,path,exp):
        self.path = path
        self.exp = exp
        self.memdirs = {}
        self.latvar,self.lonvar,self.timvar = "lat","lon","time"
        for memdir in glob(os.path.join(path,"member_[0-9]")):
            n = memdir.rindex('_')
            m = int(memdir[n + 1:])
            if(os.path.isfile(os.path.join(memdir,"ICMGG" + exp + ".nc"))):
                self.memdirs[m] = memdir

    def get_members(self):
        return self.memdirs.keys()

    def get_variables(self):
        return ensemble_store.variables.keys()

    def get_dataset(self,varname,member):
        path = os.path.join(self.memdirs[member],"ICMGG" + self.exp + ".nc")
        return netCDF4.Dataset(path,"r")

    def get_variable(self,varname,member):
        dataset = self.get_dataset(varname,member)
        result = None
        if(varname in ensemble_store.variables):
            result = dataset.variables.get(ensemble_store.variables[varname],None)
            if(not result):
                result = dataset.variables.get("var" + str(ensemble_store.codes[varname]),None)
        return result

    def get_field(self,timestep,varname,member):
        var = self.get_variable(varname,member)
        if(not var):
            return None
        vardims = len(var.shape)
        if(vardims == 3):
            if(varname == "prcum"):
                return numpy.sum(var[0:timestep + 1,:,:],axis = 0)
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
            return []
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
        return []
