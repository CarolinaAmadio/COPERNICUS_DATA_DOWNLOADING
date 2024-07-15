import pandas as pd

DS_DT_INSTR='GL_PR_GL' # dataset _ profile _ instrument

df = pd.read_csv('index_latest.txt', delimiter=',', header=5)
df1=pd.read_csv('tmp.txt',header=None)
df1.columns=['NAME']

df['prex'] = df['file_name'].str.split('/').str[-2]
df['FILE'] = df['file_name'].str.split('/').str[-1]
df['NAME'] = df['prex'].astype(str) + '/' + df['FILE']

def Is_in_Med(lat, lon):
      LN_MIN=-6
      LT_MIN=36
      LN_MAX=30
      LT_MAX=46
      return LT_MIN < lat < LT_MAX and LN_MIN < lon < LN_MAX

LIST_DROP=[]
for III, FILE in enumerate (df1.NAME):
    tmp = df[df.NAME==FILE]
    lat_min, lat_max = tmp.geospatial_lat_min ,tmp.geospatial_lat_max
    lon_min, lon_max = tmp.geospatial_lon_min ,tmp.geospatial_lon_max
    if Is_in_Med( lat_min.values[0]  , lon_min.values[0]  ):
        pass
    else:
        LIST_DROP.append(III)

Med=df1.drop(LIST_DROP)
import numpy as np
Med.index=np.arange(0,len(Med))
Med.to_csv('files_to_download.txt', index=False, header=False)

