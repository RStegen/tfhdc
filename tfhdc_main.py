# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 22:30:48 2023

@author: ronal
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