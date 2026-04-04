from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Date

SQLALCHEMY_DATABASE_URL = "sqlite:///fitness.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)

class FitnessGoal(Base):
    __tablename__ = "fitness_goals"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    description = Column(String)
    target_date = Column(Date)
    progress = Column(Integer)

Base.metadata.create_all(bind=engine)
