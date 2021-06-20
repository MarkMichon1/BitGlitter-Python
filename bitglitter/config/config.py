from sqlalchemy import Column, create_engine, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

engine = create_engine('sqlite:///config.db')
engine.connect()
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class ConfigBaseClass(Base):
    """Removing duplicate boilerplate to make the code less cluttered, and the database objects themselves easier to
    work with.
    """

    __abstract__ = True
    id = Column(Integer, primary_key=True)

    @classmethod
    def create(cls, **kw):
        obj = cls(**kw)
        session.add(obj)
        session.commit()

    def delete(self):
        session.delete(self)

    def save(self):
        session.add(self)
        session.commit()