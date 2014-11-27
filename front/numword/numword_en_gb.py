#This file is part of numword.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
'''
numword for EN_GB
'''

from .numword_en import NumWordEN


class NumWordENGB(NumWordEN):
    '''
    NumWord EN_GB
    '''

    def currency(self, val, longval=True):
        '''
        Convert to currency
        '''
        return self._split(val, hightxt=u"pound/s", lowtxt=u"pence",
            jointxt=u"and", longval=longval)

_NW = NumWordENGB()


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


def currency(value, longval=True):
    '''
    Convert to currency
    '''
    return _NW.currency(value, longval=longval)


def year(value, longval=True):
    '''
    Convert to year
    '''
    return _NW.year(value, longval=longval)
