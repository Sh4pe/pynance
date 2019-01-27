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
| `date` | Date when the transaction happened |
| `sender` | String containing the name of the sender of the transaction |
| `sender_account` | String containing the account information of the sender |
| `receiver` | String containing the name of the receiver of the transaction |
| `receiver_account` | String containing the account information of the receiver |
| `text` | Text of the transaction |
| `amount` | Amount of money that has been transferred |
| `currency` | Currency of the transaction like "EUR" or "USD" |


**Notes**:

* The `date` is the date that is given by the bank that exports data. No information on timezones is stored, since we just go with what the bank gives us.
* `sender_account` and `receiver_account` should contain everything required to uniquely identify the accounts involved. For transactions inside Europe, the IBAN should be sufficient.
* The `currency` of the transaction raw data should probably be consistent, i.e. all transactions should be stored in the same currency.