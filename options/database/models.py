from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.future import select


class Base(DeclarativeBase):
    pass


class Stocks(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, nullable=False)
    ask = Column(Float, nullable=False)
