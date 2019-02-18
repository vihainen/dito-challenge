from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import Sequence
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Navdata(Base):
    __tablename__ = 'navdata'

    id = Column(Integer, Sequence('hibernate_sequence'), primary_key=True)
    event = Column(String(255), nullable=False)
    timestamp = Column(DateTime)

    def __init__(self, event, timestamp):
        self.event = event
        self.timestamp = timestamp

    @property
    def serialize(self):
       return {
           'id': self.id,
           'event': self.event,
           'timestamp': None if self.timestamp == None else self.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
       }
