# Central script to choose what to do
import sys
from FeeDistribution import confirmed, unconfirmed, fees, database, export

def help():
	print('\ncommand - description\n')
	for key, option in options.items():
		print('------------------------')
		print('{} - {}'.format(key, option['description']))

	print('\n')

options = {
	'help': {
		'description': 'List all possible commands and arguments: python run.py help',
		'functionality': help
	},
	'streamconfirmed': {
		'description': 'Continually stream information about confirmed transactions into the database: python run.py streamconfirmed',
		'functionality': confirmed.stream
	},
	'standardfees': {
		'description': 'Print out recommended fees for standard confirmation times: python run.py standardfees',
		'functionality': fees.standard_fees
	},
	'recommendfee': {
		'description': 'Print out a recommende fees for a transaction to be confirmed in the time specified: python run.py recommendfee [MINUTES]',
		'functionality': fees.recommended_fee
	},
	'exportblocks': {
		'description': 'Get block numbers and observed times',
		'functionality': export.get_blocks
	},
	'exportconfirms': {
		'description': '',
		'functionality': export.confirmation_times
	},
	'unconfirmedinfo': {
		'description': 'Print out information about currently unconfirmed transactions, using either \'bitcoind\' or \'blockchain\' as provider: python run.py unconfirmedinfo [PROVIDER]',
		'functionality': unconfirmed.unconfirmed
	},
	'cleandb': {
		'description': 'Rids the database of transactions older than 1 week (and invalid entries) to make recommendations more relevant to the current state of the market',
		'functionality': database.clean
	}
}

if len(sys.argv) <= 1:
	print('Please specify a command!')

elif len(sys.argv) > 3:
	print('You\'ve specified too many arguments')

else:
	command = sys.argv[1]

	if command == 'recommendfee':
		minutes = 0
		try:
			minutes = int(sys.argv[2])
			options[command]['functionality'](minutes, True)

		except:
			print('You must specify a number of minutes for your transaction to be confirmed in.')

	elif command == 'unconfirmedinfo':
		provider = 'bitcoind'
		try :
			provider = sys.argv[2]

		except:
			pass

		options[command]['functionality'](provider)

	else:
		options[command]['functionality']()
