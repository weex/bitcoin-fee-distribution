from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from time import sleep, time
from datetime import datetime
from socket import error as socket_error
from Queue import Queue
from threading import Thread
from httplib import BadStatusLine

from .settings import RPC_USER, RPC_PASSWORD, RPC_PORT, REFRESH_PERIOD, RECONNECT_PERIOD
from .transaction import Transaction
from .database import database as db, clean

session = db.session()

rpc_connection = AuthServiceProxy("http://{}:{}@127.0.0.1:{}".format(RPC_USER, RPC_PASSWORD, RPC_PORT))
queue = Queue()
latest_block_height = 0
address_url = 'https://blockchain.info/tx/'
DEBUG = True

def print_debug(obj):
    if DEBUG:
        print str(obj)

def refresh_connection():
    """Reinitializes the connection to the bitcoin RPC server."""
    global rpc_connection
    print_debug({'msg': 'start rpc_connection refresh'})
    rpc_connection = AuthServiceProxy("http://{}:{}@127.0.0.1:{}".format(RPC_USER, RPC_PASSWORD, RPC_PORT))
    print_debug({'msg': 'finished rpc_connection refresh'})
    return

def new_transactions_into_database():
    """Streams new transactions into the local database and specifies their first seen time"""
    global rpc_connection
    print_debug({'msg': 'start new_transactions_into_database'})
    refresh_connection()
    try:
        for transaction_id, transaction in rpc_connection.getrawmempool(True).items():
            #print_debug({'msg': 'processing mempool transaction', 'txid': transaction_id}) 
            # Add transactions that are not yet in the database
            # Specify current time as time they were first seen
            if not session.query(Transaction).filter(Transaction.transaction_id == transaction_id).first():
                print_debug({'msg': 'new transaction', 'txid': transaction_id})
                t = Transaction()
                t.transaction_id = transaction_id
                t.first_seen = datetime.utcnow()
                t.size = transaction['size']
                # Save fee, convert from BTC to Satoshis
                t.fee = int(transaction['fee'] * 100000000)
                t.first_seen_block = latest_block_height
                session.add(t)
        session.commit()

    except (socket_error, JSONRPCException) as ex:
        # Revive the RPC connection if there's a connection error
        print("There has been a connection error. Make sure you are running the RPC server (bitcoin core).")
        print(ex)
        sleep(RECONNECT_PERIOD)
        refresh_connection()
        return new_transactions_into_database()

    print_debug({'msg': 'finished new_transactions_into_database'})
    return

def monitor_confirmations():
    """Checks the latest block for confirmations of previously detected transactions"""
    global latest_block_height
    global rpc_connection
    global queue

    try:
        block_height = rpc_connection.getblockcount()
    except BadStatusLine:
        return

    # If this block has already been checked, wait for the next block
    if latest_block_height == block_height:
        return

    latest_block_height = block_height
    block_hash = rpc_connection.getblockhash(block_height)
    block = rpc_connection.getblock(block_hash)
    for transaction in block['tx']:
        # If the transaction is found in the database and unconfirmed, confirm it
        transaction_db = session.query(Transaction).filter(Transaction.transaction_id == transaction).\
                                                            filter(Transaction.first_confirmed == None).first()
        if transaction_db:
            print_debug({'msg': 'Transaction confirmed.',
                         'txid': transaction,
                         'block_height': block_height,
                         'block_hash': block_hash,
                         'txurl': address_url +  transaction})
            transaction_db.block_height = block_height
            transaction_db.block_hash = block_hash
            transaction_db.first_confirmed = datetime.utcnow()
            session.commit()
            queue.put(transaction)

    return

def update_transactions():
    """Fills in missing information about transactions as soon as they are confirmed"""
    global rpc_connection
    global queue
    session = db.session()
    try:
        while True:
            # queue comes from monitor connections
            transaction_id = queue.get()
            transaction_db = session.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
            transaction = rpc_connection.getrawtransaction(transaction_id, 1)
            transaction_db.input_number = len(transaction['vin'])
            transaction_db.output_number = len(transaction['vout'])

            # Save time it took to confirm the transaction in seconds
            confirmation_time = transaction_db.first_confirmed - transaction_db.first_seen
            transaction_db.confirmation_time = confirmation_time.total_seconds()

            session.commit()

    except KeyboardInterrupt:
        return


def stream():
    """Streams new transactions into the local database and
    Adds information as they are confirmed"""
    global latest_block_height
    try:
        updater = Thread(target=update_transactions)
        updater.daemon = True
        updater.start()
        # If the added transactions were lost track of before confirmation discard
        # By setting the fee to -1
        # As the confirmation time may be unreliable and skew results toward higher fees
        post_process_transactions = session.query(Transaction).filter(Transaction.first_confirmed == None
                                     ).filter(Transaction.confirmation_time == None).all()
        for transaction in post_process_transactions:
            transaction.fee = -1
            print_debug({'msg': 'Transaction appeared during gap.',
                         'txid': transaction.transaction_id,
                         'txurl': address_url +transaction.transaction_id})

        session.commit()


        # If the post-processing was interrupted in some way, make sure it is carried out on the next start
        print_debug({'msg': 'start post-processing', 'latest_block_height': latest_block_height})
        post_process_transactions = session.query(Transaction).filter(Transaction.first_confirmed != None
                                     ).filter(Transaction.confirmation_time == None).all()
        for transaction in post_process_transactions:
            # send for processing by update_transactions()
            queue.put(transaction.transaction_id)

        while True:
            print_debug({'msg': 'start cycle', 'latest_block_height': latest_block_height})
            start = time() 
            #clean()
            #print_debug({'msg': 'done cleaning', 'elapsed_time': time() - start})
            new_transactions_into_database()
            monitor_confirmations()
            print_debug({'msg': 'end cycle', 'latest_block_height': latest_block_height, 'elapsed_time': time() - start})
            sleep(max(0,REFRESH_PERIOD - (time() - start)))

    except KeyboardInterrupt:
        return

# vim: set tabstop=8:softtabstop=8:shiftwidth=8:noexpandtab
