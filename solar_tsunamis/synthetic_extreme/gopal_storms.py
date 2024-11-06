#!/usr/bin/env python3

'''
Create estimates for Gopalswamy storms
'''

import numpy as np


def v_plaw(years):
    '''
    Given an occurrence of 1/Y years, determine the approximate CME
    speed using the Gopalswamy powerlaw fitting.
    '''

