# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 12:13:18 2023

@author: Anwender
"""

import module_basic

def module(module_name = 'basic', **kwargs):
    if module_name == 'basic':
        return module_basic.Module(**kwargs)
    #elif ...
    else:
        print('{} no valid module'.format(module_name))
        raise SystemExit