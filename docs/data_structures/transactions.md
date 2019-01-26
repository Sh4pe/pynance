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