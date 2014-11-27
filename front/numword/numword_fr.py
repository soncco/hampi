# -*- coding: utf-8 -*-
#This file is part of numword.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
'''
numword for FR
'''

from .numword_eu import NumWordEU


class NumWordFR(NumWordEU):
    '''
    NumWord FR
    '''

    def _setup(self):
        '''
        Setup
        '''
        self.negword = u"moins "
        self.pointword = u"virgule"
        self.exclude_title = [u"et", u"virgule", u"moins"]
        self.mid_numwords = [
            (1000, u"mille"),
            (100, u"cent"),
            (80, u"quatre-vingts"),
            (60, u"soixante"),
            (50, u"cinquante"),
            (40, u"quarante"),
            (30, u"trente")]
        self.low_numwords = [
            u"vingt",
            u"dix-neuf",
            u"dix-huit",
            u"dix-sept",
            u"seize",
            u"quinze",
            u"quatorze",
            u"treize",
            u"douze",
            u"onze",
            u"dix",
            u"neuf",
            u"huit",
            u"sept",
            u"six",
            u"cinq",
            u"quatre",
            u"trois",
            u"deux",
            u"un",
            u"zéro"]

    def _merge(self, curr, next):
        '''
        Merge
        '''
        ctext, cnum, ntext, nnum = curr + next

        if cnum == 1:
            if nnum < 1000000:
                return next
        else:
            if ((not (cnum - 80) % 100 or not cnum % 100)
                    and nnum < 1000000 and ctext[-1] == u"s"):
                ctext = ctext[:-1]
            if (cnum < 1000 and nnum != 1000 and ntext[-1] != "s"
                    and not nnum % 100):
                ntext += "s"

        if (nnum < cnum < 100
                and nnum % 10 == 1 and cnum != 80):
            return (u"%s-et-%s" % (ctext, ntext), cnum + nnum)
        if nnum >= 1000000 or cnum >= 1000000:
            return (u"%s %s" % (ctext, ntext), cnum + nnum)
        return (u"%s-%s" % (ctext, ntext), cnum + nnum)

    def ordinal(self, value):
        '''
        Convert to ordinal
        '''
        self._verify_ordinal(value)
        if value == 1:
            return u"premier"
        word = self.cardinal(value)
        if word[-1] == u"e" or word[-1] == u"s":
            word = word[:-1]
        if word[-1] == u"f":
            word = word[:-1] + u'v'
        return word + u"ième"

    def ordinal_number(self, value):
        '''
        Convert to ordinal number
        '''
        self._verify_ordinal(value)
        out = str(value)
        out += {"1": u"er"}.get(out[-1], u"me")
        return out

    def currency(self, val, longval=True, old=False):
        '''
        Convert to currency
        '''
        hightxt = u"Euro/s"
        if old:
            hightxt = u"franc/s"
        return self._split(val, hightxt=hightxt, lowtxt=u"centime/s",
            jointxt=u"et", longval=longval)

_NW = NumWordFR()


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


def year(value):
    '''
    Convert to year
    '''
    return _NW.year(value)
