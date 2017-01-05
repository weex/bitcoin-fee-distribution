# bitcoin-fee-distribution
Graphs fee distribution for unconfirmed Bitcoin transactions

Grabs unconfirmed transactions from blockchain.info's API or the mempool of a local Bitcoin Core node and calculates the distribution of bytes of new transactions over fees/kb. 

This can be used to select a fee that will get a profit-optimizing miner to include your transaction. To do so, imagine a horizontal line at the size of block you would want to make it into, for example 750KB and choose a fee rate at or above that point on the x-axis.

Collects data about confirmed informations as they are confirmed by streaming information using the bitcoin core API.

Provides recommendations for fees if you want a transaction to be confirmed in X amount of minutes.

## Setup and usage instructions

1) Install all requirements - "pip install -r requirements.txt".

2) Go into the FeeDistribution sub-folder.

3) Create a copy of the default_settings.py file, rename it to settings.py.

4) Specifiy all values as explained by the comments throughout the file.

5) Run "run.py help" and choose the command you want to run.

6) Be aware that the "streamconfirmed" command is supposed to precede a prolonged period of data collection during which the program and bitcoin RPC server are to be left running.

7) Be also aware that to give maximally useful fee recommendations, as much data as possible should be used as determined by the time for which streamconfirmed has been run.

8) Be also aware that frequently using the cleandb command will keep recommendations as accurate as possible by removing old transactions from the database.

Tested with Python 2.7.6