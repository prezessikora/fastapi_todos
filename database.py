from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

#sql lite

SQLALCHEMY_DATABASE_URL = 'sqlite:///./todos_app.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

#psql

SQLALCHEMY_PSQL_DATABASE_URL = 'database-1.cbkm2qskgvht.us-east-1.rds.amazonaws.com'
engine_psql = create_engine(SQLALCHEMY_DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_psql)

Base = declarative_base()