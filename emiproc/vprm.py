from netCDF4 import Dataset
import cartopy.crs as ccrs
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import importlib
from datetime import datetime,timedelta
from multiprocessing import Pool
from . import utilities as util


def doit(cfg,i,interp_tot):
    inidate = datetime(2015,7,1)+timedelta(days=i)
    print("taking care of ",inidate.strftime("%Y%m%d"))
    for s,sname in zip(["GPP","RESP"],["CO2_GPP_F","CO2_RA_F"]):
        
        data_path = "/scratch/snx3000/haussaij/VPRM/input/vprm_fluxes_EU5km_"+inidate.strftime("%Y%m%d")+".nc"
        
        data_all_t = Dataset(data_path)[s][:].data
        # For GPP, multiply by -1 to avoir negative fluxes
        if 'GPP' in s:
            data_all_t *=-1
        
        for h in range(24):
            time_ = inidate + timedelta(hours=h)
            time_str = time_.strftime("%Y%m%d%H")
            print("   ",s,time_str)

            #output_path = "/scratch/snx3000/haussaij/VPRM/int2lm/"+s+"_"+time_str+".nc"
            filename_out = s+"_"+time_str+".nc"
            
            output_path = "/scratch/snx3000/haussaij/VPRM/output/"+filename_out
            if os.path.exists(output_path):
                print('exists:',output_path)
                continue

            data = data_all_t[h,:]
            out_var_area = np.zeros((cfg.cosmo_grid.ny,cfg.cosmo_grid.nx))

            for lon in range(data.shape[1]):
                for lat in range(data.shape[0]):
                    for (x,y,r) in interp_tot[lon,lat]:#[lat,lon]:
                        #vprm_dat is in umol/m^2/s. Each cell is exactly 1km^2
                        out_var_area[y,x] += data[lat,lon]*r*cfg.input_grid.dx*cfg.input_grid.dy #now out_var_area is in umol.cell-1.s-1

            with Dataset(output_path,"w") as outf:
                util.prepare_output_file(cfg.cosmo_grid,cfg.nc_metadata,outf)
                # Add the time variable
                #example_file = "/store/empa/em05/haussaij/CHE/input_che/vprm_old/vprm_smartcarb/processed/"+filename_out
                #with Dataset(example_file) as ex :
                 
                outf.createDimension("time")
                outf.createVariable(varname="time",
                                    datatype='float64',#ex["time"].datatype,
                                    dimensions=())#ex["time"].dimensions)
                outf['time'].units = 'seconds since 2015-01-01 00:00'
                outf['time'].calendar = 'proleptic_gregorian'
                #outf["time"].setncatts(ex["time"].__dict__)


                """convert unit from umol.cell-1.s-1 to kg.m-2.s-1"""
                """calculate the areas (m^^2) of the COSMO grid"""
                m_co2 = 44.01

                cosmo_area = 1.0 / cfg.cosmo_grid.gridcell_areas()
    
                out_var_area *= cosmo_area.T*1e-9*m_co2
                out_var_name = sname
                outf.createVariable(out_var_name,float,("rlat","rlon"))
                outf[out_var_name].units = "kg m-2 s-1"
                outf[out_var_name][:] = out_var_area



def get_interp_tot(cfg):
    for n,i in enumerate([6,2,4,1,3,5]):#[1,3,5,6,2,4]): # Weird order, following the README of Julia
        input_path = cfg.vprm_path %str(i) 
        with Dataset(input_path) as inf:
            interpolation = get_interpolation(cfg,inf,filename="EU"+str(i)+"_mapping.npy",inv_name="vprm")
      
            if n==0:
                x,y = inf["lat"][:].shape
                interp_tot = np.empty((x*2,y*3),dtype=object)

            if n<3:
                interp_tot[:x,n*y:(n+1)*y] = interpolation.T
            else:
                interp_tot[x:,(n-3)*y:(n-2)*y] = interpolation.T
    return interp_tot

def get_interp_5km(cfg):
    input_path = cfg.vprm_path
    with Dataset(input_path) as inf:
        interpolation = get_interpolation(cfg,inf,inv_name="vprm")
        
    return interpolation.T



def process_vprm(cfg, interpolation, country_mask, out, latname, lonname):
    """ 
    The main script for processing the VPRM inventory.
    """
    
    # if "5km" in cfg_path:
    #     interp_tot = get_interp_5km(cfg)
    # else:
    #     interp_tot = get_interp_tot(cfg)
    
    # with Pool(cfg.nprocs) as pool:
    #     pool.starmap(doit,[(i,interpolation) for i in range(31)])#range(1,10)])


    for i in range(31):
        doit(cfg,i,interpolation)

    
