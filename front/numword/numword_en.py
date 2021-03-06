#This file is part of numword.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
'''
numword for EN
'''

from .numword_eu import NumWordEU


class NumWordEN(NumWordEU):
    '''
    NumWord EN
    '''

    def _set_high_numwords(self, high):
        '''
        Set high num words
        '''
        max_val = 3 + 3 * len(high)
        for word, i in zip(high, range(max_val, 3, -3)):
            self.cards[10 ** i] = word + u"illion"

    def _setup(self):
        '''
        Setup
        '''
        self.negword = u"minus "
        self.pointword = u"point"
        self.exclude_title = [u"and", u"point", u"minus"]

        self.mid_numwords = [
            (1000, u"thousand"),
            (100, u"hundred"),
            (90, u"ninety"),
            (80, u"eighty"),
            (70, u"seventy"),
            (60, u"sixty"),
            (50, u"fifty"),
            (40, u"forty"),
            (30, u"thirty"),
            ]
        self.low_numwords = [
            u"twenty",
            u"nineteen",
            u"eighteen",
            u"seventeen",
            u"sixteen",
            u"fifteen",
            u"fourteen",
            u"thirteen",
            u"twelve",
            u"eleven",
            u"ten",
            u"nine",
            u"eight",
            u"seven",
            u"six",
            u"five",
            u"four",
            u"three",
            u"two",
            u"one",
            u"zero",
            ]
        self.ords = {
            u"one": u"first",
            u"two": u"second",
            u"three": u"third",
            u"five": u"fifth",
            u"eight": u"eighth",
            u"nine": u"ninth",
            u"twelve": u"twelfth",
            }

    def _merge(self, curr, next):
        '''
        Merge
        '''
        ctext, cnum, ntext, nnum = curr + next

        if cnum == 1 and nnum < 100:
            return next
        elif 100 > cnum > nnum:
            return (u"%s-%s" % (ctext, ntext), cnum + nnum)
        elif cnum >= 100 > nnum:
            return (u"%s and %s" % (ctext, ntext), cnum + nnum)
        elif nnum > cnum:
            return (u"%s %s" % (ctext, ntext), cnum * nnum)
        return (u"%s, %s" % (ctext, ntext), cnum + nnum)

    def ordinal(self, value):
        '''
        Convert to ordinal
        '''
        self._verify_ordinal(value)
        outwords = self.cardinal(value).split(" ")
        lastwords = outwords[-1].split("-")
        lastword = lastwords[-1].lower()
        try:
            lastword = self.ords[lastword]
        except KeyError:
            if lastword[-1] == u"y":
                lastword = lastword[:-1] + u"ie"
            lastword += u"th"
        lastwords[-1] = self._title(lastword)
        outwords[-1] = u"-".join(lastwords)
        return " ".join(outwords)

    def ordinal_number(self, value):
        '''
        Convert to ordinal num
        '''
        self._verify_ordinal(value)
        return u"%s%s" % (value, self.ordinal(value)[-2:])

    def year(self, val, longval=True):
        '''
        Convert to year
        '''
        if not (val // 100) % 10:
            return self.cardinal(val)
        return self._split(val, hightxt=u"hundred", jointxt=u"and",
            longval=longval)

    def currency(self, val, longval=True):
        '''
        Convert to currency
        '''
        return self._split(val, hightxt=u"dollar/s", lowtxt=u"cent/s",
            jointxt=u"and", longval=longval)


_NW = NumWordEN()


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
    Convert to ordinal num
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
