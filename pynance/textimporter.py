import re
import codecs

import pandas as pd
import numpy as np

from .definitions import COLUMNS


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
    try:
        df_as_is = pd.read_csv(filepath_or_buffer=filepath_or_buffer,
                               dialect=description.csv_dialect,
                               skiprows=description.skiprows,
                               encoding=description.encoding,
                               usecols=columns_to_read,
                               dtype=str)
    except ValueError as e:
        raise UnsupportedCsvFormatException(str(e))

    # construct a new DataFrame that matches the definitions
    new_df = pd.DataFrame()

    # iterate over all the columns that we want to have in the end
    for new_col_name, new_type in COLUMNS.items():

        if new_col_name in description.column_map.keys():
            old_col_name = description.column_map[new_col_name]

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

    # read the total balance with the parser as
    # provided by `description`
    final_total_balance = description.read_total_balance(filepath_or_buffer)

    amounts = new_df['amount'].values
    new_df['total_balance'] = amounts_to_balances(amounts,
                                                  final_total_balance)

    return new_df


def amounts_to_balances(amounts, final_balance):
    """
    Gives a list of balances after each transaction
    Calculated backwards, starting with the given final balance

    PARAMS:
    -------
    amounts : iterable of float
        amount transferred for each transaction. It must be ordered,
        such that the latest performed transaction is *first* in the
        list
    final_balance : float
        total value of the balance after the last transaction

    RETURNS:
    --------
    list of float
        values of the total balance after each transaction
    """

    accumulated = np.cumsum(np.array(amounts[::-1], dtype=float))[::-1]
    return accumulated - accumulated[0] + final_balance


class CsvFileDescription():
    def __init__(self,
                 column_map,
                 csv_dialect,
                 formatters,
                 skiprows,
                 encoding,
                 total_balance_re_pattern,
                 total_balance_formatter):
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
        total_balance_formatter : function : string -> float
            a function that is applied to the string matched by
            total_balance_re_pattern and return the number
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
        self.total_balance_formatter = total_balance_formatter

    def read_total_balance(self, filepath_or_buffer):
        """
        Parses a filepath or buffer for a regex given in
        total_balance_re_pattern and formats it into a number

        PARAMS:
        -------
        filepath_or_buffer : str, pathlib.Path, py._path.local.LocalPath or
            any object with a readlines() method

        RETURNS:
        --------
        number :
            total balance as specified of the type that is defined for the
            `total_balance` column using a formatter given in the
            formatters dict

        RAISES:
        -------
        UnsupportedCsvFormat :
            if the total_balance was not found in the given filepath or buffer

        """

        def read_from_buffer(buffer):

            for line in buffer.readlines():
                match = re.search(self.total_balance_re_pattern, line)
                if match:
                    formatter = self.total_balance_formatter
                    return formatter(match.group(0))

            raise UnsupportedCsvFormatException(
                'Total balance was not found in given file or stream.')

        try:
            # try to use filepath_or_buffer like a filepath
            with codecs.open(filepath_or_buffer, 'r', encoding=self.encoding) \
                    as buffer:
                return read_from_buffer(buffer)
        except (TypeError, AttributeError):
            # try to use read directly
            filepath_or_buffer.seek(0)
            return read_from_buffer(filepath_or_buffer)


class UnsupportedCsvFormatException(IOError):
    """
        An error that occurs, if the importer is asked to read a CSV file with
        a setting that does not fit the actual file
    """
    pass
