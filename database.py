from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData() #На базе мета данных создаются таблицы
#### Всё это создает базу данных ###
engine = create_engine(f"mysql+mysqlconnector://chat:Uz_ZarZyAJiOgxPp@109.174.29.40:3306/Chat?auth_plugin=mysql_native_password", pool_pre_ping=True)
engine.connect()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) #Для создания сессий
Base = declarative_base() #Нужна для объявления таблиц
metadata.create_all(engine) #Создает объявленные таблицы
