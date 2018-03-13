from sqlalchemy import create_engine
from sqlalchemy import Table, Column, DateTime, Integer, String, MetaData, ForeignKey

from sqlalchemy.sql import select

engine = create_engine('sqlite:////home/python/ionify/ion.db')
metadata = MetaData()

songs = Table('songs', metadata,
              Column('id', Integer, primary_key=True),
              Column('name', String, nullable=False),
              Column('file_location', String, nullable=False),
              Column('time_uploaded', DateTime),
              Column('played', Integer))

queue = Table('queue', metadata,
              Column('id', Integer, primary_key = True),
              Column('song_id', None, ForeignKey('songs.id')),
              Column('status', Integer),
              # 1- QUEUED, 2- PLAYED, 3- SKIPPED #
              Column('requested_by', String))

def create_databse():
    metadata.create_all(engine)
             
