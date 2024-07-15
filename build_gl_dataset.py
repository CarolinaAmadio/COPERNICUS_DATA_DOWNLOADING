import os
import glob
import sys
import numpy as np
from netCDF4 import Dataset
sys.path.append("/g100/home/userexternal/camadio0/CA_functions/")
from datetime import datetime, time
from julian_to_datetime import julARR_to_datetime
from SELECT_PROFILE import ObservationSelector, NEAREST_latlon_idxlatlon
import pandas as pd
from utils import rewriteCYCLE
from write_nc import write_nc, write_nc_from_df
from scipy.io import netcdf_file 
from scipy.interpolate import interp1d

# dynamic inputs
METHOD='MID_DAY'
METHOD='SUPEROBS'
#static inputs
VARLIST=['CPHL','DOX1','DOX2']
VARWRITE=['CPHL','DOX1','DOX2','PSAL','TEMP']
INDIR='profiles/'
OUTDIR='SUPERGLIDER/'
maskfile='/g100_work/OGS_devC/Benchmark/SETUP/PREPROC/MASK/meshmask.nc'
ncIN=Dataset(maskfile)
nav_lat = ncIN.variables['nav_lat'][:]
nav_lon = ncIN.variables['nav_lon'][:]
ncIN.close()
lon_arr=np.array(nav_lon[0,:])
lat_arr=np.array(nav_lat[:,0])
filelist=glob.glob(INDIR+'*nc')


for FILE in filelist:
    nc = Dataset(FILE)
    VAR_in_FILE = ( nc.variables.keys())
    VAR_in_FILE_set = set(VAR_in_FILE)
    VARLIST_set = set(VARLIST)
    intersection = VAR_in_FILE_set.intersection(VARLIST_set)
    if intersection: # if biogeochemistry is measured
        tmp=FILE.split('/')
        directory_name=tmp[1].split('_')[-2]
        # Check if the directory exists
        if not os.path.exists(OUTDIR +  directory_name):
            os.makedirs(OUTDIR + directory_name)
            print(f"Directory '{OUTDIR+directory_name }' created.")
        # Check if more than 1 profile per grid point
        times=nc.variables['TIME'][:]
        lat_gl,lon_gl= nc.variables['LATITUDE'][:], nc.variables['LONGITUDE'][:]
        lat_serv, lon_serv,idx_lat, idx_lon = NEAREST_latlon_idxlatlon(lat_gl,lon_gl ,lat_arr, lon_arr,nav_lat,nav_lon)
        df =pd.DataFrame(index=np.arange(0,len(idx_lat)), columns=['idx_lat', 'idx_lon'])
        df.idx_lat =idx_lat
        df.idx_lon =idx_lon 
        df['AGGREGATED_IDX'] = df.index
        serv=df.groupby(by=['idx_lat','idx_lon']) .agg({'AGGREGATED_IDX':list,})
        serv.reset_index(inplace=True)

        if len(df) == len(serv):
            print('no data to aggregate')
            for CYCLE in range(0,len(df)):
                NUMB = len(glob.glob(OUTDIR+directory_name+'/*nc'))+1
                NR_PROFILE__=rewriteCYCLE(NUMB)
                outfile =  'SD' + str(directory_name) + '_' + NR_PROFILE__ + '.nc'
                filepath=OUTDIR+directory_name +'/'+ outfile  
                ncOUT =netcdf_file( filepath ,"w")
                write_nc(ncOUT,filepath ,nc, CYCLE )  

        else:
            AGGREGATED_list = serv.AGGREGATED_IDX.sort_values()
            for LIST_AGGR in serv.AGGREGATED_IDX.sort_values():
                NUMB = len(glob.glob(OUTDIR+directory_name+'/*nc'))+1
                NR_PROFILE__=rewriteCYCLE(NUMB)
                outfile =  'SD' + str(directory_name) + '_' + NR_PROFILE__ + '.nc'
                filepath=OUTDIR+directory_name +'/'+ outfile
                ncOUT = netcdf_file( filepath ,"w")
                if len(LIST_AGGR) ==1:
                    write_nc(ncOUT,filepath ,nc, CYCLE )
                else:
                    COLUMNLIST= ['CPHL', 'DOX1', 'DOX2', 'PSAL', 'TEMP','LATITUDE','LONGITUDE','TIME','Pres']
                    df1= pd.DataFrame(index=np.arange(0,10000), columns= COLUMNLIST)
                    s_times = times[LIST_AGGR]
                    s_times=julARR_to_datetime( s_times)
                    s_lat   = lat_gl[LIST_AGGR]
                    s_lon   = lon_gl[LIST_AGGR]
                    df1['LATITUDE'].iloc[0:len(s_lat)] =s_lat
                    df1['LONGITUDE'].iloc[0:len(s_lon)] =s_lon
                    df1['TIME'].iloc[0:len(s_times)] =s_times

                    for VAR in VARWRITE:
                        if VAR in nc.variables.keys():
                           print(VAR) 
                           print(LIST_AGGR)
                           s_obs = nc.variables[VAR][:][LIST_AGGR]
                           s_qc = nc.variables[VAR+'_QC'][:][LIST_AGGR]
                           pres  = nc.variables['PRES'][:][LIST_AGGR]
                           # filtre fill values nan
                           selector = ObservationSelector(s_obs, s_times, s_qc, pres ) # classe
                           if METHOD=='MID_DAY': # aggiungi il vincolo di n obs
                              var_, times_, IDX = selector.MIDDAY()
                              valid_indices = np.where(~var_.mask)[0]
                              var_ = var_[valid_indices]
                              var_[var_ < 0] = 0.0005
                              Pres = pres[IDX] 
                              Pres = Pres[valid_indices]
                           if METHOD=='SUPEROBS': #interp and mean
                              var_, depth_ = selector.SUPEROBS()
                           
                           if  var_ is not None:
                              print("The variable 'my_variable' exists.")
                              df1[VAR].iloc[0:len(depth_)]= var_
                              df1['Pres_'+VAR]= np.nan
                              df1['Pres_'+VAR].iloc[0:len(depth_)] = depth_
                              del var_
                           else:
                              print("The variable 'myvariable' does not exist.")

                        #df1['Pres'].iloc[0:len(depth_)] = pres
                    write_nc_from_df(ncOUT,filepath ,nc, df1 ) 

# build nc dataset 3_SUPERFLOAT_WRITING.py
#/g100_work/OGS_devC/camadio/GLIDER_VALIDATION_v1/SCRIPTS
