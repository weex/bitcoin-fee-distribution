# bitcoin-fee-distribution
Graphs fee distribution for unconfirmed Bitcoin transactions

Grabs unconfirmed transactions from blockchain.info's API or the mempool of a local Bitcoin Core node and calculates the distribution of bytes of new transactions over fees/kb. 

This can be used to select a fee that will get a profit-optimizing miner to include your transaction. To do so, imagine a horizontal line at the size of block you would want to make it into, for example 750KB and choose a fee rate at or above that point on the x-axis.

# Installation

1. Copy default_settings.py to settings.py 

2. Edit settings.py to put in the path to where this will run.

# Running

Run fee_distribution.py with "--provider=bitcoind" if you want to pull the data from a local Bitcoin Core node. Otherwise it will pull the data from blockchain.info's API.

# Requirements

Python pyplot

Python numpy

Tested with Python 2.7.6

# Demo

See this in action at http://bitcoinexchangerate.org/fees
