import netCDF4 as nc
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from cycler import cycler  # for remaping the colormap
import sys
import geopy.distance as geodist
import datetime

mpl.rcParams['axes.prop_cycle'] = \
     cycler('color', ['#1f77b4', '#ff7f0e', '#2ca02c', '#404040', '#d62728',
                      '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22',
                      '#17becf'])
# totally optional, it just changes line colors in the plots
oases = ['Siwa', 'Tafilalt', "M'hamid El Ghizlane", 'Skoura', 'Adrar',
         'Seba', 'Tozir', 'Kaouar', 'Selima', "Guelta d' Archei", 'Tifariti']
lats = [29.20, 31.34, 29.83, 31.06, 28.02, 27.50, 33.91, 19.08, 21.37,
        16.91, 26.16]
lons = [25.51, -4.26, -5.72, -6.55, -0.26, 14.47, 8.12, 12.87, 29.32,
        21.77, -10.56]

# %% Land-sea mask check
ds = nc.Dataset('GRACE-CRI/LAND_MASK.CRI.nc')
landmask = ds['land_mask']
lat = ds['lat']
lon = ds['lon']
for oasis in oases:
    # Find indices in the lat - lon mask map, based on the oases coordinates
    # Use round() when lat[0] and lon[0] give the center of the cell
    # When they give the edge, use int()
    lat_index = round((lats[oases.index(oasis)] - lat[0]) / 0.5)
    lon_index = round((lons[oases.index(oasis)] - lon[0]) / 0.5)
    if landmask[lat_index, lon_index] == 0:
        sys.exit('Oasis ' + oasis + ' has a landmask of 0')
del lat, lon, landmask, ds, lat_index, lon_index, oasis

# %% Mascons-oases matching
ds = nc.Dataset('GRACE-CRI/JPL_MSCNv02_PLACEMENT.nc')
masc_id = ds['mascon_id']
lat = ds['mascon_lat']
lon = ds['mascon_lon']
masc_rad = ds['mascon_rad']
mascons = {}  # Empty directory, which will hold oases names and mascon numbers
for oasis in oases:
    i = oases.index(oasis)
    # empty array for distances between oasis and all mascons
    distance = np.zeros(len(masc_id), dtype='float')
    distance[:] = 1e4  # An arbitrary large initial number
    for j in range(0, len(masc_id)):
        # If the mascon coordinates are very far from the oasis, don't bother
        # estimating its distance. Keep only mascons at most 3 degrees away
        # Oases lons are in (-180, 180). Mascon lons are in (0, 360).
        # This is why the modulo % is used
        if (abs(lats[i]-lat[j]) < 3) and (abs(lons[i] % 360-lon[j] % 360) < 3):
            distance[j] = geodist.distance((lats[i], lons[i]),
                                           (lat[j], lon[j])).km
    # Find the index of the minimum distance mascon
    index_min = np.argmin(distance)
    # Update the dictionary with the nearest mascon for this oasis
    mascons.update({oasis: index_min})
    print(oasis, distance[index_min], masc_rad[j])

del masc_id, lat, lon, masc_rad, distance, i, j, oasis, index_min

# %% Plot the monthly liquid water equivalent anomaly, relative to 2004-2009
ds = \
   nc.Dataset('GRACE-CRI/GRCTellus.JPL.200204_202102.GLO.RL06M.MSCNv02CRI.nc')
lon = ds['lon']
lat = ds['lat']
time = ds['time']
dates = [datetime.date(2002, 1, 1) + datetime.timedelta(i) for i in time[:]]
lwe = ds['lwe_thickness']  # [time, lat, lon] in cm
error = ds['uncertainty']  # [time, lat, lon] in cm, 1-sigma uncertainty

# scale factors
ds = nc.Dataset('GRACE-CRI/CLM4.SCALE_FACTOR.JPL.MSCNv02CRI.nc')
sf = ds['scale_factor']

# Initialize all arrays we will use
grace = np.zeros((len(oases), len(time)), dtype='float')
grace[:] = np.nan
graceerr = np.zeros((len(oases), len(time)), dtype='float')
graceerr[:] = np.nan
scalefactor = np.zeros(len(oases))
scalefactor[:] = np.nan

plt.figure(figsize=(12, 8))
for i in range(0, len(oases)):
    # use of round() because I assume that lat[0] and lon[0] give the center
    # of the pixel. If they give the edge, it should use int()
    lat_index = round((lats[i] - lat[0]) / 0.5)
    lon_index = round((lons[i] - lon[0]) / 0.5)
    grace[i] = lwe[:, lat_index, lon_index]
    graceerr[i] = error[:, lat_index, lon_index]
    # Uncomment below if we want to use scale factors
    # scalefactor[i] = sf[lat_index, lon_index]
    # Uncomment below if we don't want to use scale factors
    scalefactor[i] = 1.
    plt.plot(dates, grace[i]*scalefactor[i])
    # plt.errorbar(dates, grace[i]*scalefactor[i],
    #              graceerr[i]*scalefactor[i], errorevery=3)
plt.ylim([-20, 10])
plt.legend(oases)
plt.axhline(0, color='k', linestyle=':')
