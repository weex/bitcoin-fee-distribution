#!/usr/bin/env python

#    feedistribution.py v0.1 <http://bitcoinexchangerate.org/fees> 
#    Copyright (c) 2015 David Sterry <davids@exchb.com>
#
#    Grabs unconfirmed transactions from blockchain.info's API and 
#    calculates the distribution of bytes of new transactions over fees/kb. 
#    This can be used to select a fee that will currently incentivize
#    a profit-optimizing miner to include your transaction. To do so,
#    imagine a horizontal line at the size of block you would want to
#    make it into, for example 750KB and choose a fee rate at or above
#    that point on the x-axis.
#
##########################################################################333
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys
import optparse
import urllib, json
import numpy
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from pprint import pprint
from operator import itemgetter
from time import gmtime, strftime

parser = optparse.OptionParser(usage="%prog [options]")
parser.add_option("--unconf", dest="unconf", default=True,
		help="Process only unconfirmed transactions")
parser.add_option("--provider", dest="provider", default="blockchain",
		help="Choose from 'blockchain' and 'blockrio'")
(options, args) = parser.parse_args()

num_outs = {}
num_ins = {}
fees = []
feesperkb = []
population_max_in_fraction_all = []


def get_stats( data ):
	if len(data) > 0:
		arr = numpy.array( data )
		return ( numpy.mean(arr), numpy.std(arr) )
	return "No data"

def get_fee_stats( data ):
	if len(data) > 0:
		arr = numpy.array( data )
		print "Number of transactions: " + str(len(data))
		print "Minimum fee: " + str(numpy.min(arr)/100000000.0)
		print "Average fee for payers: " + str(numpy.mean(arr)/100000000.0)
		print "Median fee for payers: " + str(numpy.median(arr)/100000000.0)
		print "Stdev of fee for payers: " + str(numpy.std(arr)/100000000.0)
	return "No data"

if options.unconf:
	raw = ''
	if options.provider == 'blockchain':
		if options.unconf:
			url = "https://blockchain.info/unconfirmed-transactions?format=json&offset="
			
		txs = []
		response = urllib.urlopen("https://blockchain.info/q/unconfirmedcount")
		unconf_count = int(response.read())
		print "Getting " + str(unconf_count) + " unconfirmed transactions."
		for i in range(unconf_count,0,-50):
			#for i in range(0,50,50):
			#print i
			response = urllib.urlopen(url+str(i));
			raw = response.read()
			#print raw[0:100]
			parsed = json.loads(raw)
			txs = txs + parsed[u'txs'] 
				
		height = "unconf" 
		block_hash = "unconf"
		data = {}
		data[u'tx'] = txs
				
total_tx = 0
has_fee = 0
prev_out_txindex = []
for tx in data[u'tx']:
	total_value = 0
	num_out = 0
	max_value = 0

	total_in_value = 0
	num_in = 0
	max_in_value = 0
	for output in tx[u'out']:
		total_value = total_value + output[u'value']
		if output[u'value'] > max_value:
			max_value = output[u'value']
		num_out = num_out + 1 

	for prev in tx[u'inputs']:
		if 'prev_out' in prev:
			prev_out_txindex.append(prev['prev_out']['tx_index'])
			in_value = prev['prev_out']['value']
			total_in_value = total_in_value + in_value
			if in_value > max_in_value:
				max_in_value = in_value
			num_in = num_in + 1 

	fee = total_in_value - total_value
	if fee > 0:
		has_fee += 1

	if num_in > 0:
		fees.append(fee)
		size = tx['size']/1000.0
		if size < 1.0:
			size = 1.0
		feesperkb.append([fee/size/100000.0,tx['size']])

	total_tx += 1

	if num_out in num_outs.keys():
		num_outs[num_out] = num_outs[num_out] + 1 
	else:
		num_outs[num_out] = 1

	if num_in in num_ins.keys():
		num_ins[num_in] = num_ins[num_in] + 1 
	else:
		num_ins[num_in] = 1


for tx in data[u'tx']:	
	tx['respends'] = 0
	if tx['tx_index'] in prev_out_txindex:
		tx['respends'] += 1
		
 
print "Total transactions: " + str(total_tx) + " No fee: " + str(total_tx - has_fee)

get_fee_stats(fees)

# calculate minimum fee/kb for inclusion in 750KB and 1MB blocks
# sort feesperkb by highest fees first, then create a cumulative sum of KBs at that fee or above

feesperkb = sorted(feesperkb, key=itemgetter(0),reverse=True)
#print str(feesperkb)

bytessofar = 0
bytesbyfee = {}
for i in feesperkb:
	if i[0] in bytesbyfee:
		bytesbyfee[i[0]] += i[1]
	else:
		bytesbyfee[i[0]] = bytessofar + i[1]
	bytessofar += i[1]

b = []
f = []

fo = open("bitcoin-fee-distribution.csv", "w")
fo.write('Unconfirmed Fee Distribution\n('+strftime("%a %d %b %Y %H:%M:%S", gmtime())+' UTC)\nmBTC/KB,KB\n')
for i in sorted(bytesbyfee, reverse=True):
	b.append(bytesbyfee[i]/1000.0)
	f.append(i)
	fo.write(str(i) + "," + str(bytesbyfee[i]/1000.0) + "\n")
fo.close()

print "Total bytes: " + str(bytessofar)

x = numpy.array(f)
y = numpy.array(b)
plt.plot(x, y, c='blue')
plt.xticks(numpy.arange(min(x), max(x), 0.1))
plt.xlim(0, 1.0)
plt.title('Unconfirmed Fee Distribution\n('+strftime("%a %d %b %Y %H:%M:%S", gmtime())+' UTC)')
plt.ylabel('Transactions (KB)')
plt.xlabel('Fee threshold (mBTC per KB)')
plt.savefig('bitcoin-fee-distribution.png')

