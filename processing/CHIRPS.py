from bil_parse import BilParser
import os
import sys
import numpy as np
# import matplotlib.pyplot as plt

oases = ['Siwa', 'Tafilalt', "M'hamid El Ghizlane", 'Skoura', 'Adrar',
         'Seba', 'Tozir', 'Kaouar', 'Selima', "Guelta d' Archei", 'Tifariti']
lats = [29.20, 31.34, 29.83, 31.06, 28.02, 27.50, 33.91, 19.08, 21.37,
        16.91, 26.16]
lons = [25.51, -4.26, -5.72, -6.55, -0.26, 14.47, 8.12, 12.87, 29.32,
        21.77, -10.56]

years = np.arange(1981, 2021)
months = np.arange(1, 13)

prec = np.zeros([len(oases), len(years), len(months)], dtype='float')
for yr in years:
    for mo in months:
        fn = 'v2p0chirps' + str(yr) + str(mo).zfill(2)
        bp = BilParser(os.path.join('CHIRPS', fn+'.hdr'))

        if bp.values.shape != (1600, 1500):
            sys.exit('Strange behavior in ', mo, yr)

        for oasis in oases:
            # use round() when ULYMAP and ULXMAP give the center of the pixel.
            # When they give the edge, use int()
            lat_index = round((float(bp.header['ULYMAP']) -
                               lats[oases.index(oasis)]) /
                              float(bp.header['YDIM']))
            lon_index = round((lons[oases.index(oasis)] -
                               float(bp.header['ULXMAP'])) /
                              float(bp.header['XDIM']))
            prec[oases.index(oasis), yr-years[0], mo-months[0]] = \
                bp.values[lat_index, lon_index]

# This would plot the change between the 10 last years and the 10 first years
# diffs = np.mean(np.sum(prec[:, -10:] - prec[:, 0:10], axis=2), axis=1)
# plt.figure(figsize=(15, 5))
# plt.bar(range(1, len(oases)+1), diffs, width=0.8, bottom=None, align='center',
#         tick_label=oases)
