from __future__ import absolute_import

import csv
import datetime
import re

import numpy as np

from .textimporter import CsvFileDescription

# DKB definitions
# for most solutions, see
# https://github.com/hamvocke/dkb2homebank/blob/master/dkb2homebank.py
# (MIT licenced)


class DKBFormatters():
    """
        contains all the static functions needed to convert a string
        as given from a DKB CSV file to all the types needed in COLUMNS
    """

    @classmethod
    def to_datetime64(cls, datestring):
        date = datetime.datetime.strptime(datestring, "%d.%m.%Y")
        return np.datetime64(date.strftime('%Y-%m-%d'))

    @classmethod
    def to_string(cls, anystring):
        # remove trailing whitespace
        return anystring.strip()

    @classmethod
    def to_float64(cls, numberstring):
        if not numberstring:
            return np.nan
        else:
            return float(numberstring.replace(".", "").replace(",", "."))

    @classmethod
    def formatter_map(cls):
        return {
            np.datetime64: cls.to_datetime64,
            str: cls.to_string,
            np.float64: cls.to_float64
        }


class DKBCsvDialect(csv.Dialect):
    """
        Statically defines what a DKBCash CSV-file looks like
    """
    delimiter = ';'
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = csv.QUOTE_MINIMAL


class SupportedCsvTypes():
    """
        Static enumeration of all the supported CSV file types, to be used
        with :func:`~textimporter.read_csv~`
    """
    DKBCash = CsvFileDescription(
        column_map={
            "date": "Wertstellung",
            "sender_account": "Kontonummer",
            "text": "Verwendungszweck",
            "amount": "Betrag (EUR)",
        },
        csv_dialect=DKBCsvDialect(),
        formatters=DKBFormatters.formatter_map(),
        skiprows=6,
        encoding="iso-8859-1",
        total_balance_re_pattern=r'(?<=Kontostand vom \d{2}.\d{2}.\d{4}:";")'
                                 r'(.*)(?= EUR";)')

    DKBVisa = CsvFileDescription(
        column_map={
            "date": "Wertstellung",
            "text": "Beschreibung",
            "amount": "Betrag (EUR)",
        },
        csv_dialect=DKBCsvDialect(),
        formatters=DKBFormatters.formatter_map(),
        skiprows=6,
        encoding="iso-8859-1",
        total_balance_re_pattern=r'(?<=Saldo:";")(.*)(?= EUR";)')
