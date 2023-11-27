# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 14:37:40 2023

@author: Anwender
"""


from tfhdc_preprocessor import Preprocessor
import tfhdc_cmd as cmd
import tfhdc_modules as tm
from pathlib import Path
import time
from dask.distributed import Client


def run(infile, write_output = True, dask_ip = False, compute_results = False):
    
    start_time = time.time()
    if dask_ip:
        print('setting up dask client')
        client = Client(dask_ip) #it's actually used in the background
        print('client set up with IP: {}'.format(dask_ip))
    else:
        print('no parallelization chosen')
    
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
    
    if compute_results:
        result = result.compute()
    
    print('starting to write output')
    
    if write_output:
        result.to_netcdf(Path(p['files']['outpath']) / p['files']['output_file'])
    end_time = time.time()

    print('Run time: {} seconds'.format(end_time - start_time))
    
    return result

    