# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 12:13:49 2023

@author: Ronald Stegen
"""

"""
Basic Module for testing. 
Runs a decay function over the input map just to create something that can emulate
geoscientifical model runs. 
"""

#!ToDo:
    #get rid of the doubled input features-rasterfiles.
    #test if instead of Datasets a dictionary of numpy arrays can be used, too.
    #create basic module template to inherit

from numpy import sqrt
import xarray as xr

class Module():
    cmd = False
    features = False
    rasterfiles = False
    
    
    def __init__(self, cmd, features, rasterfiles):
        """
        Activate the Module object and process the input files

        Parameters
        ----------
        cmd : dict
            Dictionary of relevant information.
            Just the 'tags' part of the over all dictionary.
        features : xr.Dataset
            Dataset of features to be processed.
        rasterfiles : xr.Dataset
            Dataset of various input files.
        """
        self.cmd = cmd
        self.features = features
        self.rasterfiles = rasterfiles
        self.name = self.cmd['name']
        self.rasterfiles[self.name] = 0
        self.rasterfiles[self.name + '_start'] = xr.DataArray(self.cmd['start'], 
                                                              self.rasterfiles.mask.coords).chunk(self.rasterfiles.mask.chunks)
        
        
    def calc_distance_decay(self):
        """
        Calculate the distance_decay values and store them in rasterfiles.
        
        This currently is the modelling process and the aggregator at the same time.
        """

        xrd = sqrt((-self.features.y + self.rasterfiles.y)**2 + (-self.features.x + self.rasterfiles.x)**2)
        
        res = self.rasterfiles[self.name + '_start'] * (1/2) ** (xrd / (self.cmd['decay']*1000))
        
        self.rasterfiles[self.name + '_regions'] = res.groupby(self.rasterfiles.mask).sum('stacked_y_x').rename({'mask' : 'region'})
        
        self.rasterfiles[self.name] = res.sum('index')
        
        
    def process(self):
        """
        Process the module functions.
        
        Intended as main external access point and standard over all modules.
        Will later be inherited from 

        Returns
        -------
        xr.Dataset (or whatever rasterfiles came in)
            Dataset of the results.
        """
        self.calc_distance_decay()
        
        return self.rasterfiles
        