# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 22:30:48 2023

@author: Ronald Stegen
"""

"""
This is the main call for command line calls of the tfhdc.
Currently takes 1-2 argument.
1st: input command file (i.e. ./input.yml)
2nd: ip of the dask scheduler. Optional but required if you want to parallelize. 

"""

import sys
import tfhdc_main_run as tmr

if __name__ == '__main__':
    print(sys.argv)
    file = sys.argv[1]
    if len(sys.argv) > 2:
        dask_ip = sys.argv[2]
    else:
        dask_ip = False
    tmr.run(sys.argv[1], dask_ip = dask_ip)