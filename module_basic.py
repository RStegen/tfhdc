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
        for _,i in self.features.iterrows():
            xrd = sqrt((self.rasterfiles.x - i.x)**2 + (self.rasterfiles.y -i.y )**2)
            
            self.rasterfiles[self.name] = self.rasterfiles[self.name] + self.rasterfiles[self.name + '_start'] * (1/2) ** (xrd / (self.cmd['decay'] * 1000))
            
        
    def process(self):
        self.calc_distance_decay()
        
        return self.rasterfiles
        
        #return self.rasterfiles, self.features