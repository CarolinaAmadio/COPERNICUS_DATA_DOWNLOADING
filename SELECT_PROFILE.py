import numpy as np
from datetime import datetime, time
import sys
import numpy as np
from scipy.interpolate import interp1d 

class ObservationSelector:
    def __init__(self, observations, times, qc, pres):
        """
        """
        self.observations = observations
        self.times = times
        self.qc    = qc
        self.pres  = pres

    def MIDDAY(observations, times, qc, pres):
        """
        Select obs closest to 12:00
        """
        target_time = time(12, 0)
        def time_difference(dt):
            return abs((dt.hour * 3600 + dt.minute * 60 + dt.second) -
                       (target_time.hour * 3600 + target_time.minute * 60 + target_time.second))
        closest_index = min(range(len(times)), key=lambda i: time_difference(times[i].time()))
        return observations[closest_index], times[closest_index], qc[closest_index], pres[closest_index] 




    def SUPEROBS(self):
        """
        Select a super observation, which is the average of all observations.
        we need to interpolate the data in a common ax depth that is the average distance
        between consecutive observation
        :return: Average of all observations
        """
        
        avg_depth_step = np.mean(np.diff(self.pres ))
        common_depth_axis = np.arange(self.pres.min(), self.pres.max(), avg_depth_step)
        for i in range(self.observations.shape[0]):
            print(str(i) + ' cycle starting' )
            p = self.pres[i, :]
            o = self.observations[i, :]
            q = self.qc[i,:]
            valid_indices = np.where(~o.mask)[0]
            if len(valid_indices) > 2:
               var_ =  o[valid_indices]
               p_   =  p[valid_indices]
               q_   =  q[valid_indices]
               var_[var_ < 0] = 0.0005
               mask = ~np.isin(q_, [1, 2, 5, 8]) 
               combined_mask = q_.mask | mask
               var_ =  var_[(np.where(~combined_mask)[0])]
               p_   =  p_[(np.where(~combined_mask)[0])]
               q_   =  q_ [(np.where(~combined_mask)[0])]
               
               if len(var_) > 2:
                   interpolated_observations = np.array([
                   interp1d(p_ , var_ , kind='linear', fill_value="extrapolate")(common_depth_axis)])
               else: 
                   print( str(i) + ' cycle is empty')
                   interpolated_observations = None
            else: 
               print(str(i) + ' cycle is empty')
               interpolated_observations = None
        
        if  interpolated_observations is not None: 
            average_observation = np.mean(interpolated_observations, axis=0)
            return average_observation, common_depth_axis
        else:
            average_observation= None
            common_depth_axis = None
            print("The variable 'my_variable' does not exist.")
            return average_observation, common_depth_axis


def NEAREST_latlon_idxlatlon( lat_gl,lon_gl ,lat_arr, lon_arr,nav_lat,nav_lon):
  """
  START MATCHUP: model-gliders : function use a loop to find indeces and vals of lat lon model
  that are closest to gliders points.
  input:  glider lat lon array | model lat-lon 1-d array | lat lon model (1d array)
  return: 4 arrays MODEL_LAT | MODEL_IDX | MODEL_LON | MODEL_IDX
  """
  lat_serv = np.array([])
  lon_serv = np.array([])
  idx_lat= np.array([])
  idx_lon= np.array([])

  for iii in range(0,len(lat_gl)):
    LATVAL= lat_gl[iii]
    LONVAL= lon_gl[iii]
    IDX_lat = np.argmin([ abs(lat_arr-LATVAL) ])
    IDX_lon = np.argmin([ abs(lon_arr-LONVAL) ])
    lat_serv=np.append(lat_serv,(nav_lat[IDX_lat,IDX_lon]))
    lon_serv=np.append(lon_serv,(nav_lon[IDX_lat,IDX_lon]))
    idx_lat = np.append(idx_lat,IDX_lat)
    idx_lon = np.append(idx_lon,IDX_lon)
  return(lat_serv, lon_serv,idx_lat, idx_lon)




