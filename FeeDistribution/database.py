from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime, timedelta

from settings import DATABASE_PATH
from transaction import Base, Transaction

class Database():
	def __init__(self):
		self.engine = create_engine(DATABASE_PATH)
		self.base = Base
		self.base.metadata.create_all(self.engine)
		self.session_factory = sessionmaker(bind=self.engine)
		self.session = scoped_session(self.session_factory)

database = Database()

def clean():
	"""Rid the database of entries older than one week and invalid entries"""
	session = database.session()
	current_time = datetime.utcnow()
	one_week_ago = current_time - timedelta(weeks=1)
	session.query(Transaction).filter(Transaction.first_seen < one_week_ago).delete()
	session.query(Transaction).filter(Transaction.fee == -1).delete()
	session.commit()

	print('Transactions older than one week and invalid entries have been deleted.')