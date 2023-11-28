# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 12:13:18 2023

@author: Ronald Stegen
"""

import module_basic

def module(kwargs, module_name = 'basic'):
    """
    Function to call modules based on the string given. 
    

    Parameters
    ----------
    kwargs : Dictionary
        Dictionary of module variables. Will not be unpacked in this function.
    module_name : string, optional
        Name of the module to be called. The default is 'basic'.

    Raises
    ------
    SystemExit
        If module name not valid.

    Returns
    -------
    Module object.
        Returns the module object of the chosen module.

    """
    if module_name == 'basic':
        return module_basic.Module(**kwargs)
    #elif ...
    else:
        print('{} no valid module'.format(module_name))
        raise SystemExit