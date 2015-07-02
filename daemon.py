#!/usr/bin/env python

import sys,os,time
import glob
from time import sleep 
from pprint import pprint
from subprocess import Popen, PIPE, STDOUT;
from StringIO import StringIO
from decimal import *
import json

# our configuration file - copy defaultsettings.py to settings.py and edit
from settings import * 

# setup logging

import logging
logger = logging.getLogger('coindl-monitor')
hdlr = logging.FileHandler(BASE_PATH+'/monitor.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

# Daemon - handles running bitcoind and getting results back from it
#
class Daemon :
	#bitcoind_command  = ['/home/coindl/bin/bitcoind']
	bitcoind_command  = [BITCOIND_COMMAND]

	def get_new_address(self):
		command = self.bitcoind_command[:]
		command.extend(['getnewaddress',''])
		p = Popen(command, stdout=PIPE)
		io = p.communicate()[0]
		return io.strip()

	def check(self):
		command = self.bitcoind_command[:]
		command.extend(['getgenerate'])
		p = Popen(command, stdout=PIPE)
		io = p.communicate()[0]
		if io.strip() != 'false':
			os.system("kill -9 `ps -ef | grep bitcoind | grep -v grep | awk '{print $2}'`")
			sleep(30)
			os.system("bitcoind &")
			logger.warning('Restarted bitcoind')
			sleep(300)
		else:
			logger.info('bitcoind responded')


	def list_addresses(self):
		command = self.bitcoind_command[:]
		command.extend(['getaddressesbyaccount',''])
		p = Popen(command, stdout=PIPE)
		io = p.communicate()[0]
		return json.loads(io)

	def get_transactions(self,number):
		command = self.bitcoind_command[:]
		command.extend(['listtransactions','',str(number)])
		p = Popen(command, stdout=PIPE)
		io = p.communicate()[0]
		return json.loads(io)

	def get_rawmempool(self):
		command = self.bitcoind_command[:]
		command.extend(['getrawmempool','true'])
		p = Popen(command, stdout=PIPE)
		io = p.communicate()[0]
		return json.loads(io)

	def get_estimatefee(self,blocks):
		command = self.bitcoind_command[:]
		command.extend(['estimatefee',str(blocks)])
		p = Popen(command, stdout=PIPE)
		io = p.communicate()[0]
		return io.strip()

	def send(self,address,amount):
		command = self.bitcoind_command[:]
		command.extend(['sendtoaddress',address,str(amount),'automated'])
		#print self.command
		p = Popen(command, stdout=PIPE)
		io = p.communicate()[0]
		return p.returncode  



if __name__ == "__main__":
	logger.info("Started monitor script")

	d = Daemon()
	while(1):
		d.check()
	
		print str(d.get_rawmempool())

		sleep(REFRESH_PERIOD)
