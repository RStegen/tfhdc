# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 12:13:49 2023

@author: Anwender
"""

from numpy import sqrt
import xarray as xr
#import dask

class Module():
    cmd = False
    features = False
    rasterfiles = False
    
    
    def __init__(self, cmd, features, rasterfiles):
        self.cmd = cmd
        self.features = features
        self.rasterfiles = rasterfiles
        self.name = self.cmd['name']
        #self.imp_sum = xr.DataArray(0, coords = rasterfiles.coords, chunks = rasterfiles.chunks)
        self.rasterfiles[self.name] = 0
        self.rasterfiles[self.name + '_start'] = xr.DataArray(self.cmd['start'], 
                                                              self.rasterfiles.mask.coords).chunk(self.rasterfiles.mask.chunks)
        #self.rasterfiles[self.name + '_start'] = xr.DataArray(self.cmd['start'], 
        #                                                      self.rasterfiles.mask.coords)
        
        
    def calc_distance_decay(self):

        xrd = sqrt((-self.features.y + self.rasterfiles.y)**2 + (-self.features.x + self.rasterfiles.x)**2)
        
        res = self.rasterfiles[self.name + '_start'] * (1/2) ** (xrd / (self.cmd['decay']*1000))
        
        self.rasterfiles[self.name + '_regions'] = res.groupby(self.rasterfiles.mask).sum('stacked_y_x').rename({'mask' : 'region'})
        
        self.rasterfiles[self.name] = res.sum('index')
        
        
    def process(self):
        #return self.rasterfiles, self.features
        self.calc_distance_decay()
        
        return self.rasterfiles
        