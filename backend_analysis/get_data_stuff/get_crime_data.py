# what do you need??

import urllib2
import datetime
import sqlalchemy
import re
import time

from sqlalchemy import create_engine, Sequence
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Float, DateTime, Time
from sqlalchemy.orm import sessionmaker
from random import randint
from time import sleep

# when to start

st_year = 2008
st_mon  = 01
st_day  = 01

# when to end

en_year = 2014
en_mon  = 6
en_day  = 9

count_d = 20 # number of entries to get per query (max 20 for crime-data site)

def cycle_through():

    # parse initial conditions

    cur_date   = datetime.date(st_year,st_mon,st_day)
    end_date   = datetime.date(en_year,en_mon,en_day)                       
    offset     = 0
    data       = []

    while cur_date!=end_date:
        sleep(randint(50,100)/100)

        url_name = 'http://sanfrancisco.crimespotting.org/crime-data?format=tsv&count=' \
                + str(count_d) + '&dstart=' + str(cur_date) + '&dend=' + str(cur_date) + '&offset=' + str(offset)

        # parse returned URL data            
                                    
        url_data = urllib2.urlopen(url_name)
        url_text = url_data.read()
        url_list = url_text.split('\n')
        url_list = url_list[1:]

        if url_list[-1]=='':
            url_list = url_list[0:-1]
            
        data += url_list
    
        if len(url_list)!=count_d: # if there are fewer than requested points, go to next day
            print('DATE: ' + str(cur_date) + '\t' + 'NUM CRIMES: ' + str(len(data)))
            cur_date += datetime.timedelta(days=1)
            offset    = 0
            parse_sql(data)
            data      = []
        else:
            offset += 20

# take apart the data and send to the SQL server 

def parse_sql(data):
    
    global session
                  
    for rows in data:
        ndat = rows.split('\t')
        
        crime_data = Crime(caseid = ndat[0],
            descri   = ndat[1].strip('"'),
            datecr   = ndat[2].strip('"'),
            daycr    = ndat[3],
            timecr   = ndat[4].strip('"'),
            typecr   = ndat[5],
            beatcr   = ndat[6],
            zipcr    = ndat[7],
            addre    = ndat[8],
            latcr    = ndat[9],
            loncr    = ndat[10],
            acccr    = ndat[11],
            urlcr    = ndat[12].strip('"'))
            
        # check to make sure there are not any errors in the data
        
        try:
            crime_data.caseid = int(crime_data.caseid)     
        except ValueError:
            crime_data.caseid = 0
            
        if len(crime_data.descri)>75:
            crime_data.descri = crime_data.descri[0:74]
            
        date_test = re.compile(r'^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}$')
        if bool(date_test.search(crime_data.datecr)) is False:
            crime_data.datecr = '1900-01-01 12:00:00'
            
        if len(crime_data.daycr)>10:
            crime_data.daycr = crime_data.daycr[0:9]
            
        try:
            time.strptime(crime_data.timecr,'%H:%M')
        except ValueError:
            crime_data.timecr = '12:00'
            
        if len(crime_data.typecr)>50:
            crime_data.typecr = crime_data.typecr[0:49]
            
        if len(crime_data.beatcr)>50:
            crime_data.beatcr = crime_data.beatcr[0:49]
            
        if len(crime_data.addre)>50:
            crime_data.addre = crime_data.addre[0:49]
            
        try:
            crime_data.zipcr = int(crime_data.zipcr)     
        except ValueError:
            crime_data.zipcr = 0
            
        try:
            crime_data.latcr = float(crime_data.latcr)     
        except ValueError:
            crime_data.latcr = 0.0
            
        try:
            crime_data.loncr = float(crime_data.loncr)     
        except ValueError:
            crime_data.loncr = 0.0
            
        if len(crime_data.acccr)>50:
            crime_data.acccr = crime_data.acccr[0:49]
        
        if len(crime_data.urlcr)>100:
            crime_data.urlcr = crime_data.urlcr[0:99]       
        
        session.add(crime_data)
    
    session.commit()
 
# specify method to call sql

engine = create_engine('mysql+pymysql://root@127.0.0.1/crimedb', pool_recycle=5, echo=False)

# setup schema

Base = declarative_base()

class Crime(Base):
    __tablename__ = 'crimedb1'

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

Session = sessionmaker(bind=engine)
session = Session()
        
def main():
    cycle_through()
    
if __name__ == "__main__":
    main()
    