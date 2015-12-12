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
import daemon

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
thresh750 = 0.0
thresh1000 = 0.0
est1 = 0
est6 = 0
est12 = 0
est24 = 0

def get_stats( data ):
	if len(data) > 0:
		arr = numpy.array( data )
		return ( numpy.mean(arr), numpy.std(arr) )
	return "No data"

def get_fee_stats( data ):
	if len(data) > 0:
		arr = numpy.array( data )
		print ""
		print "All fees in mBTC"
		print "Bitcoinexchangerate.org Fee Estimates --------"
		print "Minimum fee/KB for 750KB block: " + str(thresh750)
		print "Minimum fee/KB for 1MB block: " + str(thresh1000)
		print ""
		print "Bitcoin Core Fee Estimates -------------------"
		print "Blocks ---- mBTC/KB"
		print "     1      " + str(float(est1)*1000.0)
		print "     6      " + str(float(est6)*1000.0)
		print "    12      " + str(float(est12)*1000.0)
		print "    24      " + str(float(est24)*1000.0)
		print ""
		print "Statistics -----------------------------------"
		print "Minimum fee: " + str(numpy.min(arr)/100000.0)
		print "Maximum fee: " + str(numpy.max(arr)/100000.0)
		print "Average fee for payers: " + str(numpy.mean(arr)/100000.0)
		print "Median fee for payers: " + str(numpy.median(arr)/100000.0)
		print "Stdev of fee for payers: " + str(numpy.std(arr)/100000.0)
	return "No data"

def jsonify( data ):
	if len(data) > 0:
		arr = numpy.array( data )
		j = {
		 "result": "success",
		 "min_for_750k": str(thresh750),
		 "min_for_1000k": str(thresh1000),
		 "core_est_1": str(float(est1)*1000.0),
		 "core_est_6": str(float(est6)*1000.0),
		 "core_est_12": str(float(est12)*1000.0),
		 "core_est_24": str(float(est24)*1000.0),
		 "mempool_min_fee": str(numpy.min(arr)/100000.0),
		 "mempool_max fee": str(numpy.max(arr)/100000.0),
		 "mempool_avg_nonzero_fee": str(numpy.mean(arr)/100000.0),
		 "mempool_median_nonzero_fee": str(numpy.median(arr)/100000.0),
		 "mempool_stdev_nonzero_fee": str(numpy.std(arr)/100000.0),
		}
	else:
		j = {"result": "error"}
	return json.dumps(j)

if options.unconf:
	raw = ''
	txs = []
	data = {}
	if options.provider == 'blockchain':
		if options.unconf:
			url = "https://blockchain.info/unconfirmed-transactions?format=json&offset="
			
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
		data[u'tx'] = txs

	elif options.provider == 'bitcoind':
		d = daemon.Daemon()
		raw = d.get_rawmempool()
		#txs = json.loads(raw)
		data[u'tx'] = raw 
		
		est1 = d.get_estimatefee(1)
		est6 = d.get_estimatefee(6)
		est12 = d.get_estimatefee(12)
		est24 = d.get_estimatefee(24)

		# u'6d2b502eea0f8575d84eba792d811f5bb80dbeb92083111a4a8a5f500d75b788': 
		# {
		#  u'fee': 0.0001, 
		#  u'startingpriority': 8459910.32051282, 
		#  u'height': 362735, 
		#  u'depends': [], 
		#  u'time': 1435380798, 
		#  u'currentpriority': 8459910.32051282, 
		#  u'size': 226
		# }				


total_tx = 0
has_fee = 0
prev_out_txindex = []
if options.provider == 'blockchain':
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

elif options.provider == 'bitcoind':
	for txid in data[u'tx']:
		tx = data[u'tx'][txid]
		total_value = 0
		num_out = 0
		max_value = 0

		total_in_value = 0
		num_in = 0
		max_in_value = 0

		fee = tx[u'fee']*100000000.0
		if fee > 0:
			has_fee += 1
	
		fees.append(fee)
		size = tx['size']/1000.0
		feesperkb.append([fee/size/100000.0,tx['size']])
	
		total_tx += 1
	
 
print "Total transactions: " + str(total_tx) + "  No fee: " + str(total_tx - has_fee)


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
	if bytessofar > 750000 and thresh750 == 0:
		thresh750 = i[0]
	if bytessofar > 1000000 and thresh1000 == 0:
		thresh1000 = i[0]

get_fee_stats(fees)

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

j = jsonify(fees)
fj = open("bitcoin-fee-distribution.json", "w")
fj.write(j)
fj.close()

x = numpy.array(f)
y = numpy.array(b)
plt.plot(x, y, c='blue')
plt.xticks(numpy.arange(min(x), max(x), 0.2))
plt.xlim(0, 2.0)
plt.yscale('log')
plt.title('Unconfirmed Fee Distribution\n'+strftime("%a %d %b %Y %H:%M:%S", gmtime())+' UTC')
plt.ylabel('Transactions (KB)')
plt.xlabel('Fee threshold (mBTC per KB)')
plt.savefig('bitcoin-fee-distribution.png')

