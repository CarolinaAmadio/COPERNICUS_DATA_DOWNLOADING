import copernicusmarine

#INFO:  https://help.marine.copernicus.eu/en/articles/7949409-copernicus-marine-toolbox-introduction 

gl_dataset = copernicusmarine.get(
    dataset_id = 'cmems_obs-ins_ibi_phybgcwav_mynrt_na_irr' ,
    dataset_part = 'latest' ,
    username = 'camadio' ,
    password = 'Bsqx3066!!' ,
    filter = "GL_*_GL*"
    )
