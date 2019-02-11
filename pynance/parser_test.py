from __future__ import absolute_import

import unittest
import datetime
import locale

import numpy as np

from hypothesis import given
from hypothesis.strategies import datetimes, decimals

from .textimporter import DKBFormatters


class ParserTestCase(unittest.TestCase):
    """
    Contains tests that concern the safe reading of text files and
    reading data from it
    """

    @given(decimals(allow_infinity=False,
                    allow_nan=False,
                    places=2))
    def test_dkb_float_formatting1(self, decimal):
        """
        test all kinds of decimal numbers, that are formatted
        with de-DE locale
        """
        locale.setlocale(locale.LC_ALL, 'de')

        german_number_str = locale.format("%f",
                                          decimal, grouping=True)

        formatter = DKBFormatters.to_float64
        result = formatter(german_number_str)
        expected = float(decimal)
        self.assertEqual(expected, result)

    @given(datetimes(min_value=datetime.datetime(1900, 1, 1, 0, 0)))
    def test_dkb_date_formatting(self, dt):
        """
        test various dates. First format them into string,
        then let the formatter try to parse them back to datetime
        """
        datestr = dt.strftime("%d.%m.%Y")
        formatter = DKBFormatters.to_datetime64
        date_result = formatter(datestr)
        expected = np.datetime64(dt.date())

        self.assertEqual(expected, date_result)


def test_suite():
    suite = unittest.makeSuite(ParserTestCase)
    return suite
