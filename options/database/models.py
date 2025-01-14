from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.future import select
import datetime


class Base(DeclarativeBase):
    pass


class Stocks(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    ticker = Column(String, nullable=False, unique=True)


class Options(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True)
    underlying_ticker = Column(String)
    ask_price = Column(Float)
    ask_size = Column(Integer)
    strike_price = Column(Float)
    contract_type = Column(String)
    shares_per_contract = Column(Integer)
    expiration_date = Column(Date)
    delta = Column(Float)
    underlying_last_trade_price = Column(Float)
    timestamp = Column(DateTime)
