from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
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
    symbol = Column(String, nullable=False)
    strike_price = Column(Float, nullable=False)
    expiration_date = Column(String, nullable=False)
    type = Column(String, nullable=False)  # e.g., 'call' or 'put'
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    stock = relationship("Stocks", backref="options")
    delta = Column(Float, nullable=True)  # Delta value
    price = Column(Float, nullable=True)  # Current price of the option
    updated = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
