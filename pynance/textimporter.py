import csv
import datetime
import re

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
                raise UnsupportedCsvFormat("Column %s was not found in \
                                        file" % old_col_name)

            # get the formatter for the required type
            formatter = description.formatters[new_type]

            try:
                # apply the formatter
                new_col = df_as_is[old_col_name].apply(formatter)
            except:
                raise UnsupportedCsvFormat("Could not convert content of \
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

    # read the total balance with the parser provided by `description`
    final_total_balance = description.read_total_balance(filepath_or_buffer)

    amounts = new_df['amount'].values
    new_df['total_balance'] = amounts_to_balances(amounts,
                                                  final_total_balance)

    return new_df


class CsvFileDescription():
    def __init__(self,
                 column_map,
                 csv_dialect,
                 formatters,
                 skiprows,
                 encoding,
                 total_balance_re_pattern):
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
        encoding : string
            encoding of the csv file, e.g. 'utf-8' or 'iso-8859-1'
        total_balance_re_pattern : string
            regex expression, that matches for the final total balance
        """

        # check that for every type in COLUMN, there is a formatter
        for col_type in COLUMNS.values():
            assert col_type in formatters.keys()

        self.column_map = column_map
        self.csv_dialect = csv_dialect
        self.formatters = formatters
        self.skiprows = skiprows
        self.encoding = encoding
        self.total_balance_re_pattern = total_balance_re_pattern

    def read_total_balance(self, filepath_or_buffer):
        with open(filepath_or_buffer,
                  mode='r', encoding=self.encoding) as file_:

            for line in file_.readlines():
                match = re.search(self.total_balance_re_pattern, line)
                if match:
                    target_type = COLUMNS['total_balance']
                    formatter = self.formatters[target_type]
                    return formatter(match.group(0))

        raise UnsupportedCsvFormat(
            'Total balance was not found in given header.')


class UnsupportedCsvFormat(IOError):
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
    "total_balance": np.float64,
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
        encoding="iso-8859-1",
        total_balance_re_pattern=r'(?<=Kontostand vom \d{2}.\d{2}.\d{4}:";")(\d+,\d+)')

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
        total_balance_re_pattern=r'(?<=Saldo:";")(\d+,\d+)')


# def make_dkb_total_balance_parser(description, total_balance_label):
#     """
#     read the total_balance after the last transaction of a DKBCash csv-file

#     PARAMS:
#     -------
#     description : CsvFileDescription, a description of how the CSV file is to
#         be read and transformed
#     total_balance_label : str
#         label of the row to look for, when searching the total balance

#     RETURNS:
#     --------
#     func: filepath_or_buffer -> float :
#         a function that parses a given filepath_or_buffer for a total balance
#         after the last transaction in the file, which raises an IOError
#         if the total balance is not found in the given string

#     """
#     def total_balance_parser(filepath_or_buffer):
#         header = pd.read_csv(filepath_or_buffer=filepath_or_buffer,
#                              dialect=description.csv_dialect,
#                              skiprows=0,
#                              nrows=description.skiprows,
#                              encoding=description.encoding,
#                              dtype=str,
#                              error_bad_lines=False)

#         for i, row in header.iterrows():
#             if total_balance_label in row[0]:
#                 # get the balance string and strip off quotes and currency
#                 balance_str = row[1].split(' ')[0]

#                 return DKBFormatters.to_float64(balance_str)

#         # TODO: use more specific exception
#         raise IOError('Total balance was not found in given header.')

#     return total_balance_parser


def amounts_to_balances(amounts, final_balance):
    """
    Gives a list of balances after each transaction
    Calculated backwards, starting with the given final balance

    PARAMS:
    -------
    amounts : iterable of float
        amount transferred for each transaction
    final_balance : float
        total value of the balance after the last transaction

    RETURNS:
    --------
    list of float
        values of the total balance after each transaction
    """
    if len(amounts) == 1:
        return [final_balance]
    else:
        return amounts_to_balances(amounts[:-1],
                                   final_balance-amounts[-1]) \
            + [final_balance]
