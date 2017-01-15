from sqlalchemy.sql import func
from sqlalchemy import text
import csv

from .database import database as db
from .transaction import Transaction

session = db.session()

def get_blocks():
	"""
	return list of block heights and first seen times
	"""

	sql = text("select min(strftime('%s',first_confirmed)) as conf_time, block_height from transactions group by block_height")
	result = db.engine.execute(sql)
	out = []
	for row in result:
		out.append((row[0], row[1]))
	return out

def confirmation_times():
        blocks = get_blocks()
 
	sql = text("""select (julianday(first_confirmed) - julianday(first_seen)) * 86400 as conf_time,
			fee/size as fee_rate, transaction_id, block_height, fee, size,
                        strftime('%s',first_seen) as fs_timestamp
			from transactions 
			where first_confirmed is not null and fee > -1;""")
	result = db.engine.execute(sql)
	columns = {}
	out = []
	for tx in result.fetchall():
		if not columns:
			columns = tx.keys()
		row = dict(zip(columns, tx.values()))
		block_zero = None
		for b in blocks:
			(time, bh) = b

			if bh is None:
				bh = 1

			if time is None:
				continue

			# if this block was found after this transaction was seen
			if int(time) > int(row['fs_timestamp']) < int(time):
				block_zero = bh - 1
				break

		if block_zero is None:
			continue
		row['conf_blocks'] = row['block_height'] - block_zero
		out.append(row)

	columns.append('conf_blocks')	
	writer = csv.DictWriter(open('transaction_info.csv', 'w'),
				fieldnames=columns)
	writer.writeheader()
	for row in out:
		writer.writerow(row)
