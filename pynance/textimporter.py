import csv
import datetime

import pandas as pd
import numpy as np


def read_csv(filepath_or_buffer, description):
    """
    Reads the text in a csv file or buffer and converts it into a
    DataFrame as specified by a CsvFileDescription

    Parameters
    ----------
    filepath_or_buffer : str, pathlib.Path, py._path.local.LocalPath or
        any object with a read() method.
        Passed to pandas.read_csv
    description : CsvFileDescription, a description of how the CSV file is to
        be read and transformed

    Returns
    -------
    pandas.DataFrame : the data as contained in filepath_or_buffer with a
        header defined in COLUMNS. Parts of COLUMNS that have no equivalent in
        filepath_or_buffer are filled with NAN

    Raises
    ------
    UnsupportedCsvFormatException
        if the file does not contain the required header columnsd
    """
    columns_to_read = description.column_map.values()

    # read the dataframe as it is, with only strings
    # formatting is done later
    df_as_is = pd.read_csv(filepath_or_buffer=filepath_or_buffer,
                           dialect=description.csv_dialect,
                           skiprows=description.skiprows,
                           encoding=description.encoding,
                           usecols=columns_to_read,
                           dtype=str)

    # construct a new DataFrame that matches the definitions
    new_df = pd.DataFrame()

    # iterate over all the columns that we want to have in the end
    for new_col_name, new_type in COLUMNS.items():

        if new_col_name in description.column_map.keys():
            old_col_name = description.column_map[new_col_name]

            if old_col_name not in df_as_is.columns.values:
                raise UnsupportedCsvFormatException("Column %s was not found in \
                                                     file" % old_col_name)

            # get the formatter for the required type
            formatter = description.formatters[new_type]

            try:
                # apply the formatter
                new_col = df_as_is[old_col_name].apply(formatter)
            except:
                raise UnsupportedCsvFormatException("Could not convert content of \
                                                     column %s to %s"
                                                    % (old_col_name, new_type))

            new_df[new_col_name] = new_col
        else:
            # some columns are not present in the loaded csv,
            # fill them with emptyness of the correct type
            # str will still become dtype('object')
            # because that's how pandas works
            empty_series = pd.Series(dtype=new_type)
            new_df[new_col_name] = empty_series

    return new_df


class CsvFileDescription():
    def __init__(self,
                 column_map,
                 csv_dialect,
                 formatters,
                 skiprows,
                 encoding):
        """
        A description of a specific CSV file design.
        Typically a definition for a specific bank transaction CSV file
        would be defined as an instance of this class.

        Parameters
        ----------
        column_map : dict,  maps the columns  of the csv file (as keys)
            to the pynance columns (as values)
        csv_dialect : csv.Dialect, that describes the files inner syntax
        formatters : dict(type T, func: string item -> T item) that maps the
            required types
            to functions that convert an entry into that type
        skiprows : int number of rows to skip while reading the file starting
            at the beginning of the file
        """

        # check that for every type in COLUMN, there is a formatter
        for col_type in COLUMNS.values():
            assert col_type in formatters.keys()

        self.column_map = column_map
        self.csv_dialect = csv_dialect
        self.formatters = formatters
        self.skiprows = skiprows
        self.encoding = encoding


class UnsupportedCsvFormatException(IOError):
    """
        An error that occurs, if the importer is asked to read a CSV file with
        a setting that does not fit the actual file
    """
    pass


# STATIC DEFINITIONS below this line ################

# see issue #5 and #6
# use numpy types for numbers, because that's what pandas likes
COLUMNS = {
    "date": np.datetime64,
    "sender_account": str,
    "receiver_account": str,
    "text": str,
    "amount": np.float64,
    "currency": str,
    "category": str,
    "tags": str,
    "origin": str}

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
        # TODO: there is probably a better way to convert it
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
            # TODO: use some builtin package, maybe locale for this
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
        encoding="iso-8859-1")
    DKBVisa = CsvFileDescription(
        column_map={
            "date": "Wertstellung",
            "text": "Beschreibung",
            "amount": "Betrag (EUR)",
        },
        csv_dialect=DKBCsvDialect(),
        formatters=DKBFormatters.formatter_map(),
        skiprows=6,
        encoding="iso-8859-1")
