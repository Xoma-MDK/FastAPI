from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from settings import connstr

metadata = MetaData()
engine = create_engine(
    connstr, pool_pre_ping=True)
engine.connect()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

metadata.create_all(engine)
