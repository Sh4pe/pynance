# Database

## Brainstorming

* Schema evolution
* Each transaction gets an 'imported at' timestamp and a sequence number
  * Sequence number needed so that transactions can be uniquely identified.
* 'imported at' and sequence number can be a primary key
* One object to manage transactions and its storage
  * Name: `Transactions`.
* `Transactions` contains a `Storage` class that is responsible for interacting (i.g. reading and writing) with the database.

## Problems

### Total balance

The `Transactions` need to store the total balance as well. We probably want to store the total balance in each row as well.