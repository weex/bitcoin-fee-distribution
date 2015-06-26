# bitcoin-fee-distribution
Graphs fee distribution for unconfirmed Bitcoin transactions

Grabs unconfirmed transactions from blockchain.info's API and calculates the distribution of bytes of new transactions over fees/kb. 

This can be used to select a fee that will get a profit-optimizing miner to include your transaction. To do so, imagine a horizontal line at the size of block you would want to make it into, for example 750KB and choose a fee rate at or above that point on the x-axis.

# Requirements

Python pyplot
Python numpy

# Demo

See this in action at http://bitcoinexchangerate.org/fees
