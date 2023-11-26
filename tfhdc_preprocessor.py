# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 20:02:52 2023

@author: ronal
"""


from ruamel.yaml import YAML
from pathlib import Path
from osmnx import geocode_to_gdf, features_from_polygon
from pandas import concat
import rasterio
from rasterio import transform, features
import xarray as xr
import json
import hashlib

class Preprocessor(dict):
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
        self.load_and_prepare_data_dict()
        
    def load_data_dict(self):
        """
        Load the input dictionary.
        
        Intended to be run by the init process.
        """
        yaml = YAML(typ = 'safe', pure = True)
        self.update(yaml.load(Path(self.infile)))

    def prepare_files_dict(self):
        """
        Prepare the 'files' segment of the dictionary.
        
        Intended to be run by the init process.
        """
        path = Path(self.infile).parent.resolve()
        self['files'] = self.get('files', {})
        self['files']['inpath'] = path
        self['files']['base_cmd'] = self.infile
        self['files']['outpath'] = Path(self['files'].get('outpath', self['files']['inpath']) / 'output')
        self['files']['regions'] = self['files'].get('regions', 'regions.json')
        self['files']['regions_buffer'] = self['files'].get('regions_buffer', 'regions_buffer.json')
        self['files']['features'] = self['files'].get('features', 'features.json')
        self['files']['cmd'] = self['files'].get('cmd', 'cmd.json')
        self['files']['regions_raster'] = self['files'].get('regions_raster', 'regions_raster.tif')
        self['files']['rasterfiles'] = self['files'].get('rasterfiles', 'rasterfiles.nc')

    def prepare_geo_settings(self):
        """
        Prepare the 'geo' segment of the dictionary.
        
        Intended to be run by the init process.
        """
        self['geo'] = self.get('geo', {})
        self['geo']['crs'] = self['geo'].get('crs', 32632)
        self['geo']['buffer'] = self['geo'].get('buffer', 0)
        self['geo']['resolution'] = self['geo'].get('resolution', 1000)
        

    def load_and_prepare_data_dict(self):
        """
        Load and prepare the dictionary into the object. 
        
        Intended to be run by the init process.
        """        
        self.load_data_dict()
        self.prepare_files_dict()
        self.prepare_geo_settings()
        
        
    def run(self):
        """
        Core execution function.

        Doesn't require or take any additional input.
        All input is part of the already loaded input dictionary.
        """        
        self['files'].get('outpath').mkdir(parents = True, exist_ok = True)
        self.load_region_shape()
        self.load_tags()
        self.transform_crs()
        self.rasterize_regions()
        self.store_mask_to_netcdf()
        self.store_geojsons()
        self.create_hashes()
        self.save_dict_to_json()
        
        
    
    def load_region_shape(self): 
        """ 
        Load the region shape from open streetmap based on the 'regions' key in the input yaml and buffer them for the widened field of interest.
        
        Intended to be executed by the run() process.
        """
        self.region = geocode_to_gdf(self['region'])
        self.region['region_nr'] = list(range(1, len(self.region) + 1))
        c = self.region.crs
        self.region_buffer = self.region.to_crs(self['geo'].get('crs', 32632)).buffer(self['geo'].get('buffer',0)).to_crs(c)
        
            
    def load_single_tag(self, data, shape):
        """ 
        Load a single tag from open streetmap, based on the buffered regions shape.
        
        Intended to be executed by the run() process.
        """
        tags = {data['key'] : data['value']}
        gdf = features_from_polygon(shape, tags).loc['node']
        gdf = gdf.loc[gdf[data['filter']['key']].isin(data['filter']['value'])]
        gdf['decay'] = data['decay']
        return gdf
        
    def load_tags(self):
        """ 
        Iterate over the tags of interest and use the load_single_tag to download them.
        
        Intended to be executed by the run() process.
        """
        shapes = self.region_buffer.geometry.values
        self.features = concat([self.load_single_tag(self['tags'][x], shape) for x in list(self['tags']) for shape in shapes])
        
    def transform_crs(self):
        """ 
        Transform the crs of the created Geodataframes to the crs of interest.
        
        Usually epsg:32632 for central Europe/Germany.        
        Intended to be executed by the run() process.
        """
        self.region = self.region.to_crs(self['geo']['crs'])
        self.region_buffer = self.region_buffer.to_crs(self['geo']['crs'])
        self.features = self.features.to_crs(self['geo']['crs'])
        self.features['x'] = self.features.geometry.x
        self.features['y'] = self.features.geometry.y
    
    def rasterize_regions(self):
        """ 
        Rasterize the region to create the masking raster.
        
        Intended to be executed by the run() process.
        """
        bbox = self.region.total_bounds
        xmin, ymin, xmax, ymax = bbox
        res = self['geo']['resolution'] # resolution in m
        w = (xmax - xmin) // res
        h = (ymax - ymin) // res
        
        out_meta = {
            "driver": "GTiff",
            "dtype": "uint8",
            "height": h,
            "width": w,
            "count": 1,
            "crs": self.region.crs,
            "transform": transform.from_bounds(xmin, ymin, xmax, ymax, w, h),
            "compress": 'lzw'
        }
        
        outfile = self['files']['outpath'] / self['files']['regions_raster']
        with rasterio.open(outfile, 'w+', **out_meta) as out:
            out_arr = out.read(1)
            shapes = ((geom,value) for geom, value in zip(self.region.geometry, self.region.region_nr))
            rasterized = features.rasterize(shapes, fill = 0, out = out_arr, transform = out.transform)
            out.write_band(1, rasterized)
            
            
    def store_mask_to_netcdf(self):
        """ 
        Load and transform the region_buffer mask and save it to a netcdf4 database.
        
        Intended to be executed by the run() process.
        """
        
        maskfile = self['files']['outpath'] / self['files']['regions_raster']
        outfile = self['files']['outpath'] / self['files']['rasterfiles']
        with xr.open_dataset(maskfile) as ds:
            ds= ds.rename({'band_data' : 'mask'})
            ds['mask'] = ds.mask.sel(band = 1, drop = True).astype(int)
            ds= ds.drop_vars('band')
            ds.to_netcdf(outfile)
    
    def store_geojsons(self):
        """ 
        Save the GeoDataFrames as GeoJSONs.
        
        Intended to be executed by the run() process.
        """
        op = self['files'].get('outpath')
        
        with open(op / self['files'].get('regions'), 'w') as outfile:
            outfile.write(self.region.to_json())
            
        with open(op / self['files'].get('regions_buffer'), 'w') as outfile:
            outfile.write(self.region_buffer.to_json())
        
        with open(op / self['files'].get('features'), 'w') as outfile:
            outfile.write(self.features.to_json())
    
    def prepare_data_for_saving(self):
        """ 
        Prepare the dictionary data for savings.
        
        Path objects cannot be saved to json strings, thus they are transformed to strings.        
        Intended to be executed by the run() process.
        """
        self['files']['inpath'] = str(self['files'].get('inpath'))
        self['files']['outpath'] = str(self['files'].get('outpath'))
    
    def create_hashes(self):
        """ 
        Create the hashes of relevant stored files, used in later processes.
        
        regions_buffer, features and rasterfiles.
        Stores them as hexvalues in the dictionary.        
        Intended to be executed by the run() process.
        """
        self['hashes'] = {}
        
        fd = self.get('files')
        op = Path(fd.get('outpath'))
        
        with open(op / fd.get('regions_buffer'), 'rb') as f:
            h = hashlib.file_digest(f, 'sha256').hexdigest()
            self['hashes']['regions_buffer'] = h
            
        with open(op / fd.get('regions'), 'rb') as f:
            h = hashlib.file_digest(f, 'sha256').hexdigest()
            self['hashes']['regions'] = h
            
        with open(op / fd.get('features'), 'rb') as f:
            h = hashlib.file_digest(f, 'sha256').hexdigest()
            self['hashes']['features'] = h
            
        with open(op / fd.get('rasterfiles'), 'rb') as f:
            h = hashlib.file_digest(f, 'sha256').hexdigest()
            self['hashes']['rasterfiles'] = h
    
    def save_dict_to_json(self):
        """ 
        Save the dictionary to a json file.
        
        Intended to be executed by the run() process.
        """
        op = self['files'].get('outpath')
        self.prepare_data_for_saving()
        with open(op / self['files'].get('cmd'), 'w') as f:
            f.write(json.dumps(self))
            
            
            
            
            
            