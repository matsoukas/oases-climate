# oases-climate
Code for extracting and computing monthly climate data for a specific set of oases. Original data came from CHIRPS, CHIRTS, GRACE, CORDEX.

CHIRPS.py works on the v2p0chirps*.bil and v2p0chirps*.hdr files downloaded from the CHRIPS site: https://data.chc.ucsb.edu/products/CHIRPS-2.0/africa_monthly/bils/
It reads the files, selects the precipitation values for the specified locations and months and saves them in variable prec with dimensions (locations, years, months)

CHIRTS.py works on CHIRTSmax.monthly.nc file downloaded from the CHIRTSmax site: https://data.chc.ucsb.edu/products/CHIRTSmonthly/netcdf/CHIRTSmax.monthly.nc
This .py file does the same thing as CHIRPS.py, but for temperature instead of precipitation. The output is variable temp with dimensions (locations, years, months)

GRACE-CRI.py works on the files downloaded from the GRACE data site: https://podaac.jpl.nasa.gov/dataset/TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06_V2
This .py file performs a couple of sanity checks. a) Are the specified oases locations classified as land in the landmask file, as they should? b) Find the nearest mascon center to the each oasis. Is the oasis-mascon center distance comparable to the mascon radius?
Then it finds the liquid water equivalent height anomaly at each oasis location and plots them all in order to see the interannual behavior of the equivalent liquid water.
