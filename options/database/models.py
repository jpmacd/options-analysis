from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.future import select
import datetime


class Base(DeclarativeBase):
    pass


class Stocks(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    ticker = Column(String, nullable=False)
    price = Column(Float, nullable=True)


class Options(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, nullable=False)
    underlying_ticker = Column(String, nullable=False)
    ask_price = Column(Float, nullable=False)
    ask_size = Column(Integer, nullable=False)
    strike_price = Column(Float, nullable=False)
    expiration_date = Column(String, nullable=False)
    contract_type = Column(String, nullable=False)
    shares_per_contract = Column(Integer, nullable=False)
    expiration_date = Column(Date, nullable=False)
    stock = relationship("Stocks", backref="options")
    delta = Column(Float, nullable=True)
    price = Column(Float, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
