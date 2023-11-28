# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 13:14:32 2023

@author: Ronald Stegen
"""

import xarray as xr
import geopandas as gpd
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

#%% Definition of used paths and files
ppath = Path().absolute()

ipath = ppath / Path('./output')
regionsf = 'regions.json'
featuresf = 'features.json'
outputs = 'tfhdc_output.nc'

opath = ppath / Path('./output/maps')
opath.mkdir(parents = True, exist_ok = True)

#%% opening of model data

regions = gpd.read_file(ipath / regionsf)
features = gpd.read_file(ipath / featuresf)

ds = xr.open_dataset(ipath / outputs)
#%% Creation of derived values for plotting

wbr = ds.wind_basic_regions.to_dataframe()['wind_basic_regions'].unstack().drop(columns = 0)

wb = ds.wind_basic.where(ds.mask > 0)
wb.name = 'Effektstärkeeinheiten'
regions['sum'] = ds.wb.groupby(ds.mask).sum()[1:]/1000000
regions['mean'] = ds.wb.groupby(ds.mask).mean()[1:]/1000
#%% Raster Map of absolute values
fig, ax = plt.subplots()
wb.plot(ax = ax, cmap = 'YlOrRd')
regions.plot(ax = ax, facecolor = 'none', linewidth = 0.1)
ax.set_title('Intensitätsverteilung in Brandenburg')
ax.axis('off')
plt.savefig(opath / 'intverteilung.jpg', bbox_inches = 'tight', dpi = 300)


#%% Map mean and sum

fig, ax = plt.subplots(ncols = 2, figsize = (5,3))
regions.plot('sum', ax = ax[0])
regions.plot('mean', ax = ax[1])
ax[0].axis('off')
ax[1].axis('off')
plt.suptitle('Vergleich Summen- und Mittelwerte nach Landkreis')
ax[0].set_title('Summenwerte')
ax[1].set_title('Mittelwerte')
plt.savefig(opath / 'summean.jpg', bbox_inches = 'tight', dpi = 300)
