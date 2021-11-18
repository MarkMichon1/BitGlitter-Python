from sqlalchemy import Column, create_engine, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool

from pathlib import Path

engine = create_engine(f'sqlite:///{Path(__file__).resolve().parent / "config.sqlite3"}?check_same_thread=False',
                       poolclass=NullPool)
engine.connect()
Session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))
session = Session()
Base = declarative_base()


class SQLBaseClass(Base):
    """Removing duplicate boilerplate to make the code less cluttered, and the database objects themselves easier to
    work with.
    """

    __abstract__ = True
    id = Column(Integer, primary_key=True)
    query = Session.query_property()

    @classmethod
    def create(cls, **kwargs):
        object_ = cls(**kwargs)
        session.add(object_)
        session.commit()
        return object_

    def delete(self):
        session.delete(self)
        session.commit()

    def save(self):
        session.add(self)
        session.commit()


SQLBaseClass.metadata.create_all(engine)
