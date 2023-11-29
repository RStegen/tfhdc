# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 14:37:40 2023

@author: Ronald Stegen
"""


from tfhdc_preprocessor import Preprocessor
import tfhdc_cmd as cmd
import tfhdc_modules as tm
from pathlib import Path
import time
from dask.distributed import Client


def run(infile, write_output = True, dask_ip = False, compute_results = False):
    """
    Run the tfhdc model.

    Parameters
    ----------
    infile : Path
        Path to the input file.
    write_output : bool, optional
        Export the results (as netcdf4). The default is True.
    dask_ip : string, optional
        IP of the dask scheduler for parallelization. The default is False.
    compute_results : bool, optional
        Return the results as computed version. The default is False.
        Makes sense if you want to write down and return the results at the same time,
        and the size of the results is not problematic for your RAM.

    Returns
    -------
    result : xr.Dataset
        Dataset of the results and some intermediate information.

    """
    
    #!ToDo:
        # get rid of the separate features
        # run modules via a loop over 'tags'
        # make features tags sensitive
        # allow for a dictionary instead of an infile - for script based calls
        # clean up the results dataset
    
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
        'cmd' : pcmd['tags']['1'], # change with loop information
        'features' : features, # features to be integrated in rasterfiles
        'rasterfiles' : rasterfiles # rasterfiles to be handled more elegantly
        } 
    print('starting module')
    module = tm.module(kwargs)
    
    
    mid_time = time.time()

    print('Preparation time: {} seconds'.format(mid_time - start_time))
    #return rasterfiles
    print('starting_module_run')
    result = module.process()
    
    if compute_results:
        result = result.compute()
    
    print('starting to write output')
    
    # well, this is the writer right now
    if write_output:
        result.to_netcdf(Path(p['files']['outpath']) / p['files']['output_file'])
    end_time = time.time()
    
    print('Computing and saving time: {} seconds'.format(end_time - mid_time))
    print('Total run un time: {} seconds'.format(end_time - start_time))
    
    return result # use this if you want to use it for other things.

    