# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 14:37:40 2023

@author: Anwender
"""


from tfhdc_preprocessor import Preprocessor
import tfhdc_cmd as cmd
import tfhdc_modules as tm
from pathlib import Path
import dask.dataframe as dd
import tfhdc_modules as tm

def run(infile):
    p = Preprocessor(infile)
    p.run()
    
    op = Path(p['files']['outpath']) / p['files']['cmd']
    pcmd = cmd.Cmd(op)
    features, rasterfiles = pcmd.load_data()
    #features = dd.from_pandas(features, npartitions = 1)
    
    
    kwargs = {
        'cmd' : pcmd['tags']['1'],
        'features' : features,
        'rasterfiles' : rasterfiles}
    print('starting module')
    module = tm.module(kwargs)
    #return rasterfiles
    print('starting_module_run')
    result = module.process()
    
    print('starting to write output')
    
    result.compute().to_netcdf(Path(p['files']['outpath']) / p['files']['output_file'])
    
    return result

    