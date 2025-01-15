from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy import ForeignKey, Column, String, Integer, Float, DateTime, Date


class Base(DeclarativeBase):
    pass


class Stocks(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    ticker = Column(String, nullable=False, unique=True)
    quotes = relationship(
        "StocksQuote", back_populates="stock", cascade="all, delete-orphan"
    )


class Options(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True)
    underlying_ticker = Column(String)
    strike_price = Column(Float)
    contract_type = Column(String)
    shares_per_contract = Column(Integer)
    expiration_date = Column(Date)
    delta = Column(Float)
    quotes = relationship(
        "OptionsQuote", back_populates="option", cascade="all, delete-orphan"
    )


class OptionsQuote(Base):
    __tablename__ = "options_quotes"

    id = Column(Integer, primary_key=True, index=True)
    option_id = Column(Integer, ForeignKey("options.id"), nullable=False)
    timestamp = Column(DateTime)
    ask_price = Column(Float)  # Added to match the code
    ask_size = Column(Integer)  # Added to match the code
    option = relationship("Options", back_populates="quotes")


class StocksQuote(Base):
    __tablename__ = "stocks_quotes"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    timestamp = Column(DateTime)
    price = Column(Float)
    stock = relationship("Stocks", back_populates="quotes")
