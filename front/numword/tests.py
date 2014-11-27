# -*- coding: utf-8 -*-
#This file is part of numword.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from unittest import TestCase, main


class TestNumWordFR(TestCase):

    def test_cardinal(self):
        from numword.numword_fr import cardinal
        self.assertEqual(cardinal(0), u"zéro")
        self.assertEqual(cardinal(11.96), u"onze virgule quatre-vingt-seize")
        self.assertEqual(cardinal(100), u"cent")
        self.assertEqual(cardinal(100.0), u"cent")
        self.assertEqual(cardinal(121.01), u"cent-vingt-et-un virgule un")
        self.assertEqual(cardinal(3121.45),
            u"trois-mille-cent-vingt-et-un virgule quarante-cinq")

    def test_cardinal_not_a_number(self):
        from numword.numword_fr import cardinal
        error = u"type\(Ximinez\) not in \[long, int, float\]"
        with self.assertRaisesRegexp(TypeError, error):
            cardinal('Ximinez')

    def test_cardinal_number_too_big(self):
        from numword.numword_fr import cardinal
        from numword.numword_fr import NumWordFR
        max_val = NumWordFR().maxval
        number = max_val + 1
        error = u"abs\(%s\) must be less than %s" % (number, max_val)
        with self.assertRaisesRegexp(OverflowError, error):
            cardinal(number)


class TestNumWordFR_BE(TestCase):

    def test_cardinal(self):
        from numword.numword_fr_be import cardinal
        self.assertEqual(cardinal(72), u"septante-deux")
        self.assertEqual(cardinal(94), u"nonante-quatre")
        self.assertEqual(cardinal(93.79),
            u"nonante-trois virgule septante-neuf")


class TestNumWordEN(TestCase):

    def test_cardinal(self):
        from numword.numword_en import cardinal
        self.assertEqual(cardinal(11.96), u"eleven point ninety-six")
        self.assertEqual(cardinal(100), "one hundred")
        self.assertEqual(cardinal(100.0), "one hundred")
        self.assertEqual(cardinal(121.01),
            "one hundred and twenty-one point one")
        self.assertEqual(cardinal(3121.45),
            u"three thousand, one hundred and twenty-one point forty-five")

    def test_cardinal_not_a_number(self):
        from numword.numword_en import cardinal
        error = u"type\(Ximinez\) not in \[long, int, float\]"
        with self.assertRaisesRegexp(TypeError, error):
            cardinal('Ximinez')

    def test_cardinal_number_too_big(self):
        from numword.numword_en import cardinal
        from numword.numword_en import NumWordEN
        max_val = NumWordEN().maxval
        number = max_val + 1
        error = u"abs\(%s\) must be less than %s" % (number, max_val)
        with self.assertRaisesRegexp(OverflowError, error):
            cardinal(number)


class TestNumWordDE(TestCase):

    def test_cardinal(self):
        from numword.numword_de import cardinal
        tests = [
            [-1.0000100, u"minus eins Komma null"],
            [1.11, u"eins Komma eins eins"],
            [1, u"eins"],
            [11, u"elf"],
            [12, u"zwölf"],
            [21, u"einundzwanzig"],
            [29, u"neunundzwanzig"],
            [30, u"dreißig"],
            [31, u"einunddreißig"],
            [33, u"dreiunddreißig"],
            [71, u"einundsiebzig"],
            [80, u"achtzig"],
            [81, u"einundachtzig"],
            [91, u"einundneunzig"],
            [99, u"neunundneunzig"],
            [100, u"einhundert"],
            [101, u"einhunderteins"],
            [102, u"einhundertzwei"],
            [151, u"einhunderteinundfünfzig"],
            [155, u"einhundertfünfundfünfzig"],
            [161, u"einhunderteinundsechzig"],
            [180, u"einhundertachtzig"],
            [300, u"dreihundert"],
            [301, u"dreihunderteins"],
            [308, u"dreihundertacht"],
            [832, u"achthundertzweiunddreißig"],
            [1000, u"eintausend"],
            [1001, u"eintausendeins"],
            [1061, u"eintausendeinundsechzig"],
            [1100, u"eintausendeinhundert"],
            [1111, u"eintausendeinhundertelf"],
            [1500, u"eintausendfünfhundert"],
            [1701, u"eintausendsiebenhunderteins"],
            [3000, u"dreitausend"],
            [8280, u"achttausendzweihundertachtzig"],
            [8291, u"achttausendzweihunderteinundneunzig"],
            [10100, u"zehntausendeinhundert"],
            [10101, u"zehntausendeinhunderteins"],
            [10099, u"zehntausendneunundneunzig"],
            [12000, u"zwölftausend"],
            [150000, u"einhundertfünfzigtausend"],
            [500000, u"fünfhunderttausend"],
            [1000000, u"eine Million"],
            [1000100, u"eine Million einhundert"],
            [1000199, u"eine Million einhundertneunundneunzig"],
            [2000000, u"zwei Millionen"],
            [2000001, u"zwei Millionen eins"],
            [1000000000, u"eine Milliarde"],
            [2147483647, u"zwei Milliarden einhundertsiebenundvierzig"
                u" Millionen vierhundertdreiundachtzigtausend"
                u"sechshundertsiebenundvierzig"],
                [23000000000, u"dreiundzwanzig Milliarden"],
                [126000000000001, u"einhundertsechsundzwanzig Billionen eins"],
                [-121211221211111, u"minus einhunderteinundzwanzig Billionen "
                    u"zweihundertelf Milliarden zweihunderteinundzwanzig "
                    u"Millionen zweihundertelftausendeinhundertelf"],
                [1000000000000000, u"eine Billiarde"],
                [256000000000000000, u"zweihundertsechsundfünfzig Billiarden"],
                # I know the next is wrong! but what to do?
                [-2.12, u"minus zwei Komma eins zwei"],
                [7401196841564901869874093974498574336000000000,
                    u"sieben Septilliarden vierhunderteins Septillionen "
                    u"einhundertsechsundneunzig Sextilliarden "
                    u"achthunderteinundvierzig Sextillionen fünfhundertvi"
                    u"erundsechzig Quintilliarden neunhunderteins "
                    u"Quintillionen achthundertneunundsechzig Quadrilliarden "
                    u"achthundertvierundsiebzig Quadrillionen dreiundneunzig "
                    u"Trilliarden neunhundertvierundsiebzig Trillionen "
                    u"vierhundertachtundneunzig Billiarden fünfhundertvieru"
                    u"ndsiebzig Billionen dreihundertsechsunddreißig "
                    u"Milliarden"],
                ]
        for number, word in tests:
            self.assertEqual(cardinal(number), word)

    def test_year(self):
        from numword.numword_de import year
        tests = [
            # Watch out, negative years are broken!
            [0, u"null"],
            [33, u"dreiunddreißig"],
            [150, u"einhundertfünfzig"],
            [160, u"einhundertsechzig"],
            [1130, u"elfhundertdreißig"],
            [1999, u"neunzehnhundertneunundneunzig"],
            [1984, u"neunzehnhundertvierundachtzig"],
            [2000, u"zweitausend"],
            [2001, u"zweitausendeins"],
            [2010, u"zweitausendzehn"],
            [2012, u"zweitausendzwölf"],
            ]
        for number, word in tests:
            self.assertEqual(year(number), word)

    def test_currency(self):
        from numword.numword_de import currency
        tests = [
            [12222, u"einhundertzweiundzwanzig Euro und zweiundzwanzig Cent"],
            [123322, u"eintausendzweihundertdreiunddreißig Euro und "
                u"zweiundzwanzig Cent"],
            [686412,
                u"sechstausendachthundertvierundsechzig Euro und zwölf Cent"],
            [84, u"vierundachtzig Cent"],
            [1, u"ein Cent"],
            ]
        for number, word in tests:
            self.assertEqual(currency(number), word)

    def test_ordinal(self):
        from numword.numword_de import ordinal
        tests = [
            [1, u"erste"],
            [3, u"dritte"],
            [11, u"elfte"],
            [12, u"zwölfte"],
            [21, u"einundzwanzigste"],
            [29, u"neunundzwanzigste"],
            [30, u"dreißigste"],
            [31, u"einunddreißigste"],
            [33, u"dreiunddreißigste"],
            [71, u"einundsiebzigste"],
            [80, u"achtzigste"],
            [81, u"einundachtzigste"],
            [91, u"einundneunzigste"],
            [99, u"neunundneunzigste"],
            [100, u"einhundertste"],
            [101, u"einhunderterste"],
            [102, u"einhundertzweite"],
            [151, u"einhunderteinundfünfzigste"],
            [155, u"einhundertfünfundfünfzigste"],
            [161, u"einhunderteinundsechzigste"],
            [180, u"einhundertachtzigste"],
            [300, u"dreihundertste"],
            [301, u"dreihunderterste"],
            [308, u"dreihundertachte"],
            [832, u"achthundertzweiunddreißigste"],
            [1000, u"eintausendste"],
            [1001, u"eintausenderste"],
            [1061, u"eintausendeinundsechzigste"],
            [2000001, u"zwei Millionen erste"],
            # The following is broken
            #[1000000000, "eine Milliardeste"],
            [2147483647, u"zwei Milliarden einhundertsiebenundvierzig"
                u" Millionen vierhundertdreiundachtzigtausend"
                u"sechshundertsiebenundvierzigste"],

            ]
        for number, word in tests:
            self.assertEqual(ordinal(number), word)


class TestNumWordES(TestCase):

    def test_cardinal(self):
        from numword.numword_es import cardinal
        self.assertEqual(cardinal(0), u"cero")
        self.assertEqual(cardinal(11.96), u"once punto noventa y seis")
        self.assertEqual(cardinal(100), u"cien")
        self.assertEqual(cardinal(100.0), u"cien")
        self.assertEqual(cardinal(121.01), u"ciento veintiuno punto uno")
        self.assertEqual(cardinal(3121.45),
            u"tres mil ciento veintiuno punto cuarenta y cinco")

    def test_cardinal_not_a_number(self):
        from numword.numword_es import cardinal
        error = u"type\(Ximinez\) not in \[long, int, float\]"
        with self.assertRaisesRegexp(TypeError, error):
            cardinal('Ximinez')

    def test_cardinal_number_too_big(self):
        from numword.numword_es import cardinal
        from numword.numword_es import NumWordES
        max_val = NumWordES().maxval
        number = max_val + 1
        error = u"abs\(%s\) must be less than %s" % (number, max_val)
        with self.assertRaisesRegexp(OverflowError, error):
            cardinal(number)

if __name__ == '__main__':
    main()
