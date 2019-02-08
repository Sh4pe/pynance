# Data formats of transactions

This document describes the data formats the transactions are
stored in. This is the main data structure because it contains
the raw data of all transactions in one bank account.

## General considerations

The transactions shall be stored as Pandas DataFrames. 

In order to determine the columns stored for transaction raw 
data, one has to take into account

* which columns make sense and
* which columns are provided by possible data sources.

This section contains a survey of columns provided by possible
data sources.

### Survey of CSV based data sources

| Source  | Kind  | Columns  |
|---|---|---|
| DKB  | Checking account, webpage  | Buchungstag, Wertstellung, Buchungstext, Auftraggeber / Begünstigter, Verwendungszweck, Kontonummer, BLZ, Betrag (EUR), Gläubiger-ID, Mandatsreferenz, Kundenreferenz |
| DKB  | Credit card, webpage       | Umsatz abgerechnet und nicht im Saldo enthalten, Wertstellung, Belegdatum, Beschreibung, Betrag (EUR), Ursprünglicher Betrag  |
| Consorsbank  | Checking account, webpage | Buchung, Valuta, Sender / Empfänger, IBAN / Konto-Nr., BIC / BLZ, Buchungstext, Verwendungszweck, Betrag in EUR |
| MoneyMoney  | Banking application | Datum, Wertstellung, Kategorie, Name, Verwendungszweck, Konto, Bank, Betrag, Währung  |

## Columns

These are the columns contained in the main data structure
of the transactions.

| Column | Description |
|--------|-------------|
| `index` | Ascenting integer that uniquely identifies the transaction |
| `imported_at` | Unix timestamp of the time when this transaction was imported |
| `date` | Date when the transaction happened |
| `sender_account` | String containing the account information of the sender |
| `receiver_account` | String containing the account information of the receiver |
| `text` | Text of the transaction |
| `amount` | Amount of money that has been transferred |
| `total_balance` | Total balance of the `receiver_account` after this transaction |
| `currency` | Currency of the transaction like "EUR" or "USD" |
| `category` | String containing the category of the transaction. May be empty. |
| `tags` | List of strings containing tags of the transaction. May be empty |


**Notes**:

* Index is an `int`, starting at 0. We probably use the `INTEGER AUTOINCREMENT` feature of sqlite for this.
* The `date` is the date that is given by the bank that exports data. No information on timezones is stored, since we just go with what the bank gives us.
* `sender_account` and `receiver_account` should contain everything required to uniquely identify the name of the sender and the accounts involved. For transactions inside Europe, the name and IBAN should be sufficient.
* The `currency` of the transaction raw data should probably be consistent, i.e. all transactions should be stored in the same currency.