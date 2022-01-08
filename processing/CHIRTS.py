import netCDF4 as nc
import numpy as np
# import matplotlib.pyplot as plt

oases = ['Siwa', 'Tafilalt', "M'hamid El Ghizlane", 'Skoura', 'Adrar',
         'Seba', 'Tozir', 'Kaouar', 'Selima', "Guelta d' Archei", 'Tifariti']
lats = [29.20, 31.34, 29.83, 31.06, 28.02, 27.50, 33.91, 19.08, 21.37,
        16.91, 26.16]
lons = [25.51, -4.26, -5.72, -6.55, -0.26, 14.47, 8.12, 12.87, 29.32,
        21.77, -10.56]

years = np.arange(1983, 2017)
months = np.arange(1, 13)

ds = nc.Dataset('CHIRTS/CHIRTSmax.monthly.nc')
lat = ds['latitude']
lon = ds['longitude']
data = ds['Tmax']

temp = np.zeros([len(oases), len(years), len(months)], dtype='float')
for oasis in oases:
    # use round() when lat[0] and lon[0] give the center of the pixel
    # When they give the edge, use int()
    lat_index = round((lats[oases.index(oasis)] - lat[0]) / 0.05)
    lon_index = round((lons[oases.index(oasis)] - lon[0]) / 0.05)
    temp[oases.index(oasis)] = np.reshape(data[:, lat_index, lon_index],
                                          (len(years), len(months)))

# This would plot the change between the 10 last years and the 10 first years
# diffs = np.mean(temp[:, -10:] - temp[:, :10], axis=(1, 2))
# plt.figure(figsize=(15, 5))
# plt.bar(range(1, len(oases)+1), diffs, width=0.8, bottom=None, align='center',
#         tick_label=oases, color='r')
