import os
import netCDF4 as nc
import pickle
import numpy as np

oases = ['Siwa', 'Tafilalt', "M'hamid El Ghizlane", 'Skoura', 'Adrar',
         'Seba', 'Tozir', 'Kaouar', 'Selima', "Guelta d' Archei", 'Tifariti']
oasesfns = ['SIWA', 'TAFILAT', 'ELGHIZLANE', 'SKOURA', 'ADRAR', 'SEBA',
            'TOZIR', 'KAOUAR', 'SELIMA', 'GUELTAARCHEI', 'TIFARITI']
elevs = np.array([-12, 773, 553, 1228, 260, 329, 50, 393, 263, 681, 487])
press = 1013.25 * (1. - 2.25577E-5*elevs)**5.25588
# Source https://www.engineeringtoolbox.com/air-altitude-pressure-d_462.html
qus = ['temperature', 'maximum temperature', 'minimum temperature',
       'precipitation', 'evaporation', 'dew point', 'wind speed']
qufolders = ['Temperature', 'TMAX', 'TMIN', 'Precipitation', 'Evaporation',
             'Humidity', 'Wind']
qufns_cordex = ['TAS', 'TMAX', 'TMIN', 'PR', 'EVAPORATION', 'SH', 'WIND']
qufns_gem = ['T2m', 'TMAX', 'TMIN', 'PR', 'EV', 'SH2m', 'uv']
quvars_his = ['tas', 'tasmax', 'tasmin', 'pr', 'evspsbl', 'huss', 'sfcWind']
quvars_rcp = ['tas', 'tmax', 'tmin', 'pr', 'evspsbl', 'huss', 'sfcWind']
quvars_gem = ['tas', 'tasmax', 'tasmin', 'pr', 'hfls', 'huss', 'v']
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
          'Nov', 'Dec']
years = np.arange(1990, 2020)

# %% Data read and averaging
# Initialization of the gem data tables for saving
gem_ba = np.zeros([len(qus), len(oases), len(years), len(months)],
                  dtype='float')
gem_85 = np.zeros([len(qus), len(oases), len(years), len(months)],
                  dtype='float')

# Initialization of the CORDEX data tables for saving
for root_his, dirs, files_his in os.walk('../data/RCM_CORDEX_Historical/TAS',
                                         topdown=True):
    pass  # Just populate root, dirs, files
models_his = [f.split('_')[1] for f in files_his]
models_his.sort()

for root_85, dirs, files_85 in os.walk('../data/RCM_CORDEX_RCP8.5/TAS',
                                       topdown=True):
    pass
models_85 = [f.split('_')[1] for f in files_85]
models_85.sort()
if models_85 != models_his:
    print('Error in matching historical and rcp8.5 data')
models = models_his

for root_26, dirs, files_26 in os.walk('../data/RCM_CORDEX_RCP2.6/TAS',
                                       topdown=True):
    pass
models_26 = [f.split('_')[1] for f in files_26]
models_26.sort()

del models_his, models_85, dirs, files_his, files_85, files_26
del root_his, root_26, root_85

cordex_ba = np.zeros([len(qus), len(oases), len(years), len(months),
                      len(models)], dtype='float')
cordex_85 = np.zeros([len(qus), len(oases), len(years), len(months),
                      len(models)], dtype='float')
cordex_26 = np.zeros([len(qus), len(oases), len(years), len(months),
                     len(models)], dtype='float')
for k in np.arange(0, len(qus)):
    qu = qus[k]
    quvar_his = quvars_his[k]
    quvar_rcp = quvars_rcp[k]

    # CORDEX Data
    qufn = qufns_cordex[k]
    for model in models:
        fn_his = os.path.join('../data/RCM_CORDEX_Historical', qufn,
                              qufn + '_' + model + '_historical.nc')
        ds_his = nc.Dataset(fn_his)
        data_his = ds_his[quvar_his + '9005']

        fn_85 = os.path.join('../data/RCM_CORDEX_RCP8.5', qufn,
                             qufn + '_' + model + '_rcp85.nc')
        ds_85 = nc.Dataset(fn_85)
        data_85 = ds_85[quvar_rcp + '0620']
        data_his = np.concatenate((data_his, data_85[:, :-12]), axis=1)
        data_85 = ds_85[quvar_rcp + '7100']  # Reuse data_85

        if model in models_26:
            fn_26 = os.path.join('../data/RCM_CORDEX_RCP2.6', qufn,
                                 qufn + '_' + model + '_rcp26.nc')
            ds_26 = nc.Dataset(fn_26)
            data_26 = ds_26[quvar_rcp + '7100']
        else:
            data_26 = np.full_like(data_85, np.nan)

        if k in (0, 1, 2):
            data_his = data_his-273.15
            data_85 = data_85[:]-273.15
            if model in models_26:
                data_26 = data_26[:]-273.15
        elif k in (3, 4):
            data_his = data_his*60*60*24*30.4375  # From kg/m2/s to mm/mon
            data_85 = data_85[:]*60*60*24*30.4375
            if model in models_26:
                data_26 = data_26[:]*60*60*24*30.4375
        elif k == 5:
            qh = data_his
            # Calculation of the relative humidity
            # ds = nc.Dataset('/home/christos/Documents/Papers/NotPublished/'
            #                 'Oases/Temperature_cur/' + oasis + '_cur_T2m.nc')
            # temp = ds['tas'][:]-273.15
            # data = pressures[oasis]*qh/(.378*qh + 0.622)/ \
            #       (6.11*10**(7.5*temp/(237.3 + temp))) * 100.
            # Calculation of the dew point
            e = (qh/(0.378*qh + 0.622)).T*press
            e = e.T
            data_his = 237.3*np.log10(e/6.11)/(7.5-np.log10(e/6.11))

            qh = data_85[:]
            e = (qh/(0.378*qh + 0.622)).T*press
            e = e.T
            data_85 = 237.3*np.log10(e/6.11)/(7.5-np.log10(e/6.11))
            if model in models_26:
                qh = data_26[:]
                e = (qh/(0.378*qh + 0.622)).T*press
                e = e.T
                data_26 = 237.3*np.log10(e/6.11)/(7.5-np.log10(e/6.11))
        elif k == 6:
            data_his = data_his  # in m/s
            data_85 = data_85[:]
            if model in models_26:
                data_26 = data_26[:]
        if np.count_nonzero(np.isnan(data_his)) > 0:
            print("Missing value in historical" + model)
        if np.count_nonzero(np.isnan(data_85)) > 0:
            print("Missing value in RCP8.5" + model)
        if (model in models_26) and (np.count_nonzero(np.isnan(data_26)) > 0):
            print("Missing value in RCP2.6" + model)

        cordex_ba[k, :, :, :, models.index(model)] = \
            np.reshape(data_his, (len(oases), len(years), len(months)))
        cordex_85[k, :, :, :, models.index(model)] = \
            np.reshape(data_85, (len(oases), len(years), len(months)))
        cordex_26[k, :, :, :, models.index(model)] = \
            np.reshape(data_26, (len(oases), len(years), len(months)))

    # gem Data
    qufolder = qufolders[k]
    qufn = qufns_gem[k]
    quvar = quvars_gem[k]
    for oasis in oasesfns:
        fn_his = os.path.join('../data/GEM', qufolder + '_cur',
                              oasis + '_cur_' + qufn + '.nc')
        ds_his = nc.Dataset(fn_his)
        fn_85 = os.path.join('../data/GEM', qufolder + '_fut',
                             oasis + '_fut_' + qufn + '.nc')
        ds_85 = nc.Dataset(fn_85)
        if k in (0, 1, 2):
            data_his = ds_his[quvar][:]-273.15  # K to C
            data_85 = ds_85[quvar][:]-273.15
        elif k == 3:
            data_his = ds_his[quvar][:]*1000*60*60*24*30.4375  # m/s to mm/mon
            data_85 = ds_85[quvar][:]*1000*60*60*24*30.4375
        elif k == 4:
            data_his = ds_his[quvar][:]*60*60*24*30.4375/2.265E6
            # W/m2 to mm/mon
            data_85 = ds_85[quvar][:]*60*60*24*30.4375/2.265E6
        elif k == 5:
            qh = ds_his[quvar][:]
            # Calculation of the dew point
            e = (qh/(0.378*qh + 0.622)).T*press[oasesfns.index(oasis)]
            # e = pressures[oasis]*qh/(0.378*qh + 0.622)
            data_his = 237.3*np.log10(e/6.11)/(7.5-np.log10(e/6.11))

            qh = ds_85[quvar][:]
            e = (qh/(0.378*qh + 0.622)).T*press[oasesfns.index(oasis)]
            data_85 = 237.3*np.log10(e/6.11)/(7.5-np.log10(e/6.11))
        elif k == 6:
            data1 = ds_his['u'][:]
            if np.count_nonzero(np.isnan(data1)) > 0:
                print("Missing value in " + oasis)
            data2 = ds_his['v'][:]
            if np.count_nonzero(np.isnan(data2)) > 0:
                print("Missing value in " + oasis)
            data_his = np.sqrt(data1**2 + data2**2)  # *0.514444  # knt to m/s

            data1 = ds_85['u'][:]
            if np.count_nonzero(np.isnan(data1)) > 0:
                print("Missing value in " + oasis)
            data2 = ds_85['v'][:]
            if np.count_nonzero(np.isnan(data2)) > 0:
                print("Missing value in " + oasis)
            data_85 = np.sqrt(data1**2 + data2**2)
        if np.count_nonzero(np.isnan(data_his)) > 0:
            print("Missing value in " + oasis)
        if np.count_nonzero(np.isnan(data_85)) > 0:
            print("Missing value in " + oasis)

        gem_ba[k, oasesfns.index(oasis), :, :] = \
            np.reshape(data_his, (len(years), len(months)))
        gem_85[k, oasesfns.index(oasis), :, :] = \
            np.reshape(data_85, (len(years), len(months)))

# Join GEM with the CORDEX models
gem_ba.resize(gem_ba.shape + (1,))
cordex_ba = np.concatenate((cordex_ba, gem_ba), axis=-1)
gem_85.resize(gem_85.shape + (1,))
cordex_85 = np.concatenate((cordex_85, gem_85), axis=-1)
cordex_26 = np.concatenate((cordex_26, np.full_like(gem_85, np.nan)), axis=-1)
models.append('GEM')
cordex_ba[-1, :, :, :, -1] = np.nan  # The wind speed of GEM is removed
cordex_85[-1, :, :, :, -1] = np.nan
with open('data.pkl', 'wb') as f:
    pickle.dump([qus, oases, years, months, models, cordex_ba, cordex_85,
                 cordex_26], f)
