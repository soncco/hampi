# -*- coding: utf-8 -*-
#This file is part of numword.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
'''
numword for FR_BE
'''

from .numword_fr import NumWordFR


class NumWordFRBE(NumWordFR):
    '''
    NumWord FR_BE
    '''

    def _setup(self):
        '''
        Setup
        '''
        super(NumWordFRBE, self)._setup()
        self.mid_numwords.insert(3, (70, u"septante"))
        self.mid_numwords.insert(2, (90, u"nonante"))

_NW = NumWordFRBE()


def cardinal(value):
    '''
    Convert to cardinal
    '''
    return _NW.cardinal(value)


def ordinal(value):
    '''
    Convert to ordinal
    '''
    return _NW.ordinal(value)


def ordinal_number(value):
    '''
    Convert to ordinal number
    '''
    return _NW.ordinal_number(value)
