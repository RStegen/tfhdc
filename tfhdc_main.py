# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 22:30:48 2023

@author: ronal
"""

import sys
from tfhdc_preprocessor import Preprocessor

if __name__ == '__main__':
    p = Preprocessor(sys.argv[1])
    p.run()