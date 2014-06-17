# call subroutines

import sqlalchemy


from sqlalchemy import create_engine, Sequence
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Float, DateTime, Time


# specify method to call sql

engine = create_engine('mysql+pymysql://root@127.0.0.1/test', pool_recycle=5, echo=False)

# setup schema

Base = declarative_base()

class Crime(Base):
     __tablename__ = 'crimedb3'

     id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
     caseid   = Column(Integer)
     descri   = Column(String(75))
     datecr   = Column(DateTime)
     daycr    = Column(String(10))
     timecr   = Column(Time)
     typecr   = Column(String(50))
     beatcr   = Column(String(50))
     zipcr    = Column(Integer)
     addre    = Column(String(50))
     latcr    = Column(Float)
     loncr    = Column(Float)
     acccr    = Column(String(50))
     urlcr    = Column(String(100))

     # spit out the entry if asked 
     def __repr__(self):
        return ("<Crime:(\n\tcaseid  = '%d'\n\tdescrip = '%s'\n\tdatecr  = '%s' \
        \n\tdaycr   = '%s'\n\ttimecr  = '%s'\n\ttypecr  = '%s' \n\tbeatcr  = '%s'\
        \n\tzipcr   = '%d'\n\taddre   = '%s' \n\tlatcr   = '%.4f'\n\tloncr   = '%.4f'\
        \n\tacccr   = '%s'\n\turlcr   = '%s')>" % (self.caseid,self.descri,self.datecr,
        self.daycr,self.timecr,self.typecr,self.beatcr,self.zipcr,self.addre,self.latcr,
        self.loncr,self.acccr,self.urlcr))
        
        
# create that table!
        
Base.metadata.create_all(engine)

# create a session to talk to SQL

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)

session = Session()

# test adding some data

crime_test = Crime(caseid = 140289281,
     descri   = 'PETTY THEFT FROM A BUILDING',
     datecr   = '2014-06-05 12:00:00',
     daycr    = 'Thursday',
     timecr   = '12:00',
     typecr   = 'THEFT',
     beatcr   = '',
     zipcr    = '',
     addre    = '',
     latcr    = 37.729194,
     loncr    = -122.430771,
     acccr    = 'Unknown',
     urlcr    = 'http://sanfrancisco.crimespotting.org/crime/2014-06-05/Theft/6290738')
     
try:
    crime_test.zipcr = int(crime_test.zipcr)     
except ValueError:
    crime_test.zipcr = 0
     
session.add(crime_test)

# stop talking to the server

session.commit()
