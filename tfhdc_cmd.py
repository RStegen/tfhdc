# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 15:36:03 2023

@author: Anwender
"""

import json
import hashlib
from pathlib import Path
import geopandas as gpd
import xarray as xr

class Cmd(dict):
    """
    Class to create and store the preprocessing information.
    Inherits dictionary and basically behaves like it with a few additions.
    
    For usage create Preprocessor object with cmd file (yaml format) as input.
    Then use Preprocessor.run() to let the preprocessing steps run and store the output files.
    The object will then contain/be the complete cmd dictionary and 
    the GeoDataFrames (region, region_buffer and features)
    and the string/path given as input file (infile)
    """
    
    region = False
    region_buffer = False
    features = False
    infile = False
    opath = False
    
    def __init__(self, infile):
        """
        Supercede the dictionary __init__.
        
        Load the input yaml into a dictionary,
        prepare optional inputs. 
        
            
        Parameters
        ----------
        infile : Path or string
            Input command file - yaml format.
        """
        super().__init__()
        self.infile = infile
        self.load_cmd_dict()
        
        self.opath = Path(self['files'].get('outpath'))
        
    def load_cmd_dict(self):
        """
        Load the input dictionary.
        
        Intended to be run by the init process.
        """
        with open(self.infile, 'r') as f:
            self.update(json.load(f))
            
    def check_hashes(self, items = ['features', 'rasterfiles']):
        """
        Check the hash values of relevant files.
        """
        
        for i in items:
            file = self['files'].get(i)
            hashs = self['hashes'].get(i)
            
            with open(self.opath / file, 'rb') as f:
                h = hashlib.file_digest(f, 'sha256').hexdigest()
                if h == hashs:
                    print('Hash value  {} tested successfully.'.format(self.opath / file))
                else:
                    print('Wrong hash value for {} - aborting.'.format(self.opath / file))
                    raise SystemExit
            
    def read_and_return_data(self, items = ['features', 'rasterfiles']):
        """
        Read and return the input files defined by the cmd file.
        
        Returns
        -------
        Dictionary of opened files.
        """
        
        data = {}
        
        for i in items:
            file = self['files'].get(i)
            
            if '.json' in file:
                features = gpd.read_file(self.opath / file)[['id','x','y']]
                data[i] = xr.Dataset.from_dataframe(features).chunk({'index' : self['chunks']['index']})
            elif '.nc' in file:
                data[i] = xr.open_dataset(self.opath / file, chunks = self['chunks'])
                
        return data
            
    def load_data(self, items = ['features', 'rasterfiles']):
        """
        Process the loading and hash validating functions

        Parameters
        ----------
        items : list of strings, optional
            List of names of files in the cmd dictionary (files and hashes) to process. 
            The default is ['features', 'rasterfiles'].

        Returns
        -------
        Requested opened files.

        """
        
        self.check_hashes(items)
        data = self.read_and_return_data(items)
        
        return [data[i] for i in items]