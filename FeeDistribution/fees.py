from sqlalchemy.sql import func

from .database import database as db
from .transaction import Transaction

session = db.session()

def calculate_fee_factor():
	"""Calculates a factor which, multiplied with a certain amount of time
	Yields a recommended fee rate in satoshis / byte"""
	avg_fee_total = session.query(func.avg(Transaction.fee)).filter(Transaction.fee != None).filter(Transaction.fee != -1).filter(Transaction.confirmation_time != None).scalar()
	avg_size_total = session.query(func.avg(Transaction.size)).filter(Transaction.fee != None).filter(Transaction.fee != -1).filter(Transaction.confirmation_time != None).scalar()
	avg_convirmation_time = session.query(func.avg(Transaction.confirmation_time)).filter(Transaction.fee != -1).filter(Transaction.fee != None).filter(Transaction.confirmation_time != None).scalar()

	# Divide average transaction fee by average transaction size
	# Yields average fee rate in satoshis / byte
	# Multiply by average confirmation time
	# Yields satoshis * seconds / byte
	return (avg_fee_total / avg_size) * avg_convirmation_time

factor = 0
# If there are no transactions in the db, the factor stays at 0
try:
	factor = calculate_fee_factor() # in satoshis / byte * second

except:
	pass

def recommended_fee(minutes, print_result=False, alternative_time=''):
	"""Calculates a recommended fee for a transaction that is supposed to be confirmed
	in #minutes minutes."""
	seconds = minutes * 60
	recommendation = str(factor / seconds)
	if print_result: print('For a transaction to be confirmed in {} minutes{}, a fee of {} satoshis / byte is recommended.'.format(minutes, alternative_time, recommendation))

	return recommendation

def standard_fees():
	"""Prints out recommended fees for standard confirmation times"""
	standard_times = [
		[10, ''],
		[1*60, ' or 1 hour'],
		[4*60, ' or 4 hours'],
		[24*60, ' or 24 hours'],
		[72*60, ' or 72 hours']
	]
	for conf_time in standard_times:
		recommended_fee(conf_time[0], True, conf_time[1])

	return