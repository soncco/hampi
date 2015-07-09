# -*- coding: utf-8 -*-
#This file is part of numword.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
'''
numword for ES
'''

from .numword_eu import NumWordEU

#TODO correct orthographics
#TODO error messages


class NumWordES(NumWordEU):
    '''
    NumWord ES
    '''

    def __init__(self):
        self.gender_stem = None
        super(NumWordES, self).__init__()

    #TODO Is this sufficient??
    def _set_high_numwords(self, high):
        '''
        Set high numwords
        '''
        max_val = 3 + 6 * len(high)

        for word, i in zip(high, range(max_val, 3, -6)):
            self.cards[10 ** (i - 3)] = word + u"illón"

    def _setup(self):
        '''
        Setup
        '''
        lows = [u"cuatr", u"tr", u"b", u"m"]
        self.high_numwords = self._gen_high_numwords([], [], lows)
        self.negword = u"menos "
        self.pointword = u"con"
        self.gender_stem = u"o"
        self.exclude_title = [u"y", u"menos", u"punto"]
        self.mid_numwords = [
            (1000, u"mil"),
            (100, u"cien"),
            (90, u"noventa"),
            (80, u"ochenta"),
            (70, u"setenta"),
            (60, u"sesenta"),
            (50, u"cincuenta"),
            (40, u"cuarenta"),
            (30, u"treinta"),
            ]
        self.low_numwords = [
            u"veintinueve",
            u"veintiocho",
            u"veintisiete",
            u"veintiseis",
            u"veinticinco",
            u"veinticuatro",
            u"veintitres",
            u"veintidos",
            u"veintiuno",
            u"veinte",
            u"diecinueve",
            u"dieciocho",
            u"diecisiete",
            u"dieciseis",
            u"quince",
            u"catorce",
            u"trece",
            u"doce",
            u"once",
            u"diez",
            u"nueve",
            u"ocho",
            u"siete",
            u"seis",
            u"cinco",
            u"cuatro",
            u"tres",
            u"dos",
            u"uno",
            u"cero",
            ]
        self.ords = {
            1: u"primer",
            2: u"segund",
            3: u"tercer",
            4: u"cuart",
            5: u"quint",
            6: u"sext",
            7: u"septim",
            8: u"octav",
            9: u"noven",
            10: u"décim",
            }

    def _merge(self, curr, next):
        '''
        Merge
        '''
        ctext, cnum, ntext, nnum = curr + next

        if cnum == 1:
            if nnum < 1000000:
                return next
            ctext = u"un"
        elif cnum == 100:
            ctext += u"t" + self.gender_stem

        if nnum < cnum:
            if cnum < 100:
                return (u"%s y %s" % (ctext, ntext), cnum + nnum)
            return (u"%s %s" % (ctext, ntext), cnum + nnum)
        elif (not nnum % 1000000) and cnum > 1:
            ntext = ntext[:-3] + u"ones"

        if nnum == 100:
            if cnum == 5:
                ctext = u"quinien"
                ntext = u""
            elif cnum == 7:
                ctext = u"sete"
            elif cnum == 9:
                ctext = u"nove"
            ntext += u"t" + self.gender_stem + u"s"
        else:
            ntext = u" " + ntext

        return (ctext + ntext, cnum * nnum)

    def ordinal(self, value):
        '''
        Convert to ordinal
        '''
        self._verify_ordinal(value)
        try:
            return self.ords[value] + self.gender_stem
        except KeyError:
            return self.cardinal(value)

    def ordinal_number(self, value):
        '''
        Convert to ordinal number
        '''
        self._verify_ordinal(value)
        # Correct for fem?
        return u"%s°" % value

    def currency(self, val, longval=True, old=False):
        '''
        Convert to currency
        '''
        if old:
            return self._split(val, hightxt=u"peso/s", lowtxt=u"peseta/s",
                divisor=1000, jointxt=u"y", longval=longval)
        return super(NumWordES, self).currency(val, jointxt=u"y",
            longval=longval)

_NW = NumWordES()


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


def currency(value, longval=True, old=False):
    '''
    Convert to currency
    '''
    return _NW.currency(value, longval=longval, old=old)


def year(value, longval=True):
    '''
    Convert to year
    '''
    return _NW.year(value, longval=longval)
