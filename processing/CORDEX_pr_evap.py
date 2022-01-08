import os
import netCDF4 as nc
import pickle
import numpy as np

oases = ['Siwa', 'Tafilalt', "M'hamid El Ghizlane", 'Skoura', 'Adrar',
         'Seba', 'Tozir', 'Kaouar', 'Selima', "Guelta d' Archei", 'Tifariti']
oasesfns = ['SIWA', 'TAFILAT', 'ELGHIZLANE', 'SKOURA', 'ADRAR', 'SEBA',
            'TOZIR', 'KAOUAR', 'SELIMA', 'GUELTAARCHEI', 'TIFARITI']
qus = ['precipitation', 'evaporation']
qufolders = ['Precipitation', 'Evaporation']
qufns = ['PR', 'EVAPORATION']
quvars = ['pr', 'evspsbl']

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
          'Nov', 'Dec']
years_ba = np.arange(1951, 2021)
years_rcp = np.arange(2021, 2101)

# %% Data read and averaging
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

cordex_ba = np.zeros([len(qus), len(oases), len(years_ba), len(months),
                      len(models)], dtype='float')
cordex_85 = np.zeros([len(qus), len(oases), len(years_rcp), len(months),
                      len(models)], dtype='float')
cordex_26 = np.zeros([len(qus), len(oases), len(years_rcp), len(months),
                     len(models)], dtype='float')
for k in np.arange(0, len(qus)):
    qu = qus[k]
    quvar = quvars[k]
    qufn = qufns[k]
    for model in models:
        fn_his = os.path.join('../data/RCM_CORDEX_Historical', qufn,
                              qufn + '_' + model + '_historical_all.nc')
        ds_his = nc.Dataset(fn_his)
        data_his = ds_his[quvar + '5105']

        fn_85 = os.path.join('../data/RCM_CORDEX_RCP8.5', qufn,
                             qufn + '_' + model + '_rcp85_all.nc')
        ds_85 = nc.Dataset(fn_85)
        data_85 = ds_85[quvar + '0600']
        data_his = np.concatenate((data_his, data_85[:, :180]), axis=1)
        data_85 = data_85[:, 180:]  # Reuse data_85

        if model in models_26:
            fn_26 = os.path.join('../data/RCM_CORDEX_RCP2.6', qufn,
                                 qufn + '_' + model + '_rcp26_all.nc')
            ds_26 = nc.Dataset(fn_26)
            data_26 = ds_26[quvar + '2100']
        else:
            data_26 = np.full_like(data_85, np.nan)

        data_his = data_his*60*60*24*30.4375  # From kg/m2/s to mm/mon
        data_85 = data_85[:]*60*60*24*30.4375
        if model in models_26:
            data_26 = data_26[:]*60*60*24*30.4375

        if np.count_nonzero(np.isnan(data_his)) > 0:
            print("Missing value in historical" + model)
        if np.count_nonzero(np.isnan(data_85)) > 0:
            print("Missing value in RCP8.5" + model)
        if (model in models_26) and (np.count_nonzero(np.isnan(data_26)) > 0):
            print("Missing value in RCP2.6" + model)

        cordex_ba[k, :, :, :, models.index(model)] = \
            np.reshape(data_his, (len(oases), len(years_ba), len(months)))
        cordex_85[k, :, :, :, models.index(model)] = \
            np.reshape(data_85, (len(oases), len(years_rcp), len(months)))
        cordex_26[k, :, :, :, models.index(model)] = \
            np.reshape(data_26, (len(oases), len(years_rcp), len(months)))

with open('data_pr_evap.pkl', 'wb') as f:
    pickle.dump([qus, oases, years_ba, years_rcp, months, models,
                 cordex_ba, cordex_85, cordex_26], f)
