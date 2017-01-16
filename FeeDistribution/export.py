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
            first_seen_block,
            (block_height - first_seen_block) as conf_block
            from transactions 
            where first_confirmed is not null and
                  first_seen_block != 0 and 
                  fee > -1;""")
    result = db.engine.execute(sql)
    columns = {}
    out = []
    for tx in result.fetchall():
        if not columns:
            columns = tx.keys()
        row = dict(zip(columns, tx.values()))
        out.append(row)

    writer = csv.DictWriter(open('transaction_info.csv', 'w'),
                fieldnames=columns)
    writer.writeheader()
    for row in out:
        writer.writerow(row)

#def fee_estimates()
#    sql = text("select (block_height - first_seen_block) as conf_block, avg(fee/size) from transactions where block_height is not null and block_height != 0 and first_seen_block != 0 group by conf_block;"	
