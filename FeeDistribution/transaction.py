from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Transaction(Base):
	__tablename__ = 'transactions'
	id = Column(Integer, primary_key=True)
	transaction_id = Column(String, index=True) # in hex
	input_number = Column(Integer)
	output_number = Column(Integer)
	size = Column(Integer) # in bytes
	fee = Column(Integer) # in total satoshis
	first_seen = Column(DateTime)
	first_seen_block = Column(Integer)
	first_confirmed = Column(DateTime)
	confirmation_time = Column(Integer)
	block_height = Column(Integer)
	block_hash = Column(String)

	def __repr__(self):
		return self.transaction_id
