from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()
engine = create_engine(
    f"mysql+mysqlconnector://chat:Uz_ZarZyAJiOgxPp@109.174.29.40:3306/Chat?auth_plugin=mysql_native_password", pool_pre_ping=True)
engine.connect()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

metadata.create_all(engine)
