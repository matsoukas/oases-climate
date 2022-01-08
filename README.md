# oases-climate
Code for extracting and computing monthly climate data for a specific set of oases. Original data came from CHIRPS, CHIRTS, GRACE, CORDEX, GEM.

processing/CHIRPS.py works on the v2p0chirps*.bil and v2p0chirps*.hdr files downloaded from the CHRIPS site: https://data.chc.ucsb.edu/products/CHIRPS-2.0/africa_monthly/bils/
It reads the files, selects the precipitation values for the specified locations and months and saves them in variable prec with dimensions [locations, years, months]

processing/CHIRTS.py works on CHIRTSmax.monthly.nc file downloaded from the CHIRTSmax site: https://data.chc.ucsb.edu/products/CHIRTSmonthly/netcdf/CHIRTSmax.monthly.nc
This .py file does the same thing as CHIRPS.py, but for temperature instead of precipitation. The output is variable temp with dimensions [locations, years, months]

processing/GRACE-CRI.py works on the files downloaded from the GRACE data site: https://podaac.jpl.nasa.gov/dataset/TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06_V2
This .py file performs a couple of sanity checks. a) Are the specified oases locations classified as land in the landmask file, as they should? b) Find the nearest mascon center to the each oasis. Is the oasis-mascon center distance comparable to the mascon radius?
Then it finds the liquid water equivalent height anomaly at each oasis location and plots them all in order to see the interannual behavior of the equivalent liquid water.

processing/CORDEX.py processes the CORDEX data (in files in ../data/RCM_CORDEX_) and the GEM data (in files ../data/GEM). It separates the data in the baseline, 'RCP8.5', and 'RCP2.6' periods. Moreover, it performs all necessary unit conversions. At the end, it saves its output in 'data.pkl', a pickle format file that can be read with the command:
with open('data.pkl', 'rb') as f:
    qus, oases, years, months, models, cordex_ba, cordex_85, cordex_26 = pickle.load(f)
where:
- qus: A list of the names of our climatological quantities. Temps are in Celsius, Precip and evaporation are in mm/month, wind speed is in m/s
- oases: A list of the names of our oases
- years: A list of the 30 baseline years
- months: A list of the 3-letter month names
- models: A list of the 9 CORDEX models + 'GEM' at the end (not a member of CORDEX)
- cordex_ba: 'ba' for baseline. A numpy array with the climatological data. Its dimensions are [len(qus), len(oases), len(years), len(months), len(models)]. If one wants the dew point temperature from model 'NOAA-GFDL-GFDL-ESM2M' for Skoura in Nov 1992, it would be cordex_ba[5, 3, 2, 10, 8]. 5 is the index number of dew point, 3 is the index number of Skoura, 2 is the index number of 1992, 10 is the index number of Nov, 8 is the index number of the NOAA model.
- cordex_85: The same as cordex_ba, but the years are now the 30 years starting from 2071 for the rcp85 scenario
- cordex_26 : Same as cordex_85, but for rcp2.6. It has a lot of np.nan because only 3 cordex models run the rcp2.6 scenario

processing/CORDEX_pr_evap.py is similar to CODEX.py. Its differences are that it works only on precipitation and evaporation data, it does not work with GEM data, and its baseline, 'RCP8.5', and 'RCP2.6' periods are defined differently. It saves its output in 'data_pr_evap.pkl', which can be read with the command:
with open('data_pr_evap.pkl', 'rb') as f:
    qus, oases, years_ba, years_rcp, months, models, cordex_ba, cordex_85, cordex_26 = pickle.load(f)
where:
- qus = ['precipitation', 'evaporation']
- oases is a list with the oases order and names
- years_ba is a list with the names of the years in the baseline. Now this is 1951-2020.
- years_rcp is a list with the names of the remaining years 2021-2100
- months: A list of the 3-letter month names
- models: A list of the 9 CORDEX models
- cordex_ba: 'ba' for baseline. A numpy array with the climatological data. Its dimensions are [len(qus), len(oases), len(years), len(months), len(models)].
- cordex_85: The same as cordex_ba, but the years are now the 80 years starting from 2021 for the rcp85 scenario
- cordex_26 : Same as cordex_85, but for rcp2.6. It has a lot of np.nan because only 3 cordex models run the rcp2.6 scenario        

The plotting/.py files produce the figures in the manuscript.
