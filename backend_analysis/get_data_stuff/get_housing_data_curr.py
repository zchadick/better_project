# what do you need??

import urllib2
import sqlalchemy
import re
import string

from sqlalchemy                 import create_engine, Sequence
from sqlalchemy                 import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types           import Float, Date
from sqlalchemy.orm             import sessionmaker
from bs4                        import BeautifulSoup
from sf_zipcodes                import zip_code
from random                     import randint
from time                       import sleep


# parse through individual houses

def parse_somestuff(ihouse):

    global session    
    
    hparsed = str(ihouse)
    
    # get address information
    
    try:
        address = ihouse.find('span',{'itemprop':'streetAddress'}).string
        if len(address)>100:
            address = address[:99]
    except:
        address = 'problem here'
    
    # get zipcode information
    
    try:
        zipcode = int(ihouse.find('span',{'itemprop':'postalCode'}).string)
    except:
        zipcode = 0
    
    # get size of lot
    
    try:
        lot_s = ihouse.find('dt',{'class':'property-lot'}).string
        lot_s = int(string.join(re.findall(r'\d+',lot_s)).replace(' ',''))
    except:
        lot_s = 0
    
    # get latitude of house
    
    try:
        h_lat = ihouse.find('meta',{'itemprop':'latitude'})
        h_lat = float(h_lat['content'])
    except:
        h_lat = 0.0
    
    # get longitude of house
    
    try:
        h_long  = ihouse.find('meta',{'itemprop':'longitude'})
        h_long  = float(h_long['content'])
    except:
        h_long = 0.0
    
    # get and parse sale date
    
    try:
        temp_d  = ihouse.find('dt',{'class':'sold-date'}).string
        temp_d  = re.findall(r'\d+',temp_d)
    
        new_d   = []
        for dates in temp_d:
            new_d.append(int(dates))
    
        sale_d  = str(new_d[2]%2000+2000) + '-' + str(new_d[0]).zfill(2) + '-' + str(new_d[2]).zfill(2)
    except:
        sale_d  = '1900-01-01'
    
    # get and parse house properties (sqft and bedrooms)
    
    try:
        temp_d  = str(ihouse.find('dt',{'class':'property-data'}))
        temp_d  = re.findall(r'\d+',str(temp_d).replace(',',''))
    
        bed_d   = int(temp_d[0])
        
        if bed_d>50:
            bed_d=0
            
        sqft_d  = int(temp_d[-1])
    except:
        bed_d   = 0
        sqft_d  = 0
    
    # get zillow ID 
    
    try:
        id_ind  = hparsed.find('id=')
        id_d    = int(hparsed[id_ind+9:id_ind+17])
    except:
        id_d    = 0
    
    # get and parse sale price
    
    try:
        s_ind   = hparsed.find('Sold:')
        p_temp  = hparsed[s_ind+6:]
        s_end   = p_temp.find('<')
        t_price = p_temp[:s_end]
        price_s = string.join(re.findall(r'[-+]?\d*\.\d+|\d+',t_price)).replace(' ','')
    
        price   = float(price_s)
    
        if t_price[-1]=='M':   
            price = price*1000000    
        elif t_price[-1]=='K':
            price = t_price*1000 
        
        price   = int(round(price))
    except:
        price = 0
    
    # place into SQL type
    
    house_data = House(houseid = id_d,
            price   = price,
            address = address,
            h_lot   = lot_s,
            h_lat   = h_lat,
            h_long  = h_long,
            h_date  = sale_d,
            h_room  = bed_d,
            h_sqft  = sqft_d,
            h_zip   = zipcode)
            
    session.add(house_data)
    
# process a single zip code

def process_code(z_code):
    global session
    
    page_num  = 19
    base_url  = 'http://www.zillow.com/san-francisco-ca-' + str(z_code) + '/sold/'
    url_name  = base_url + str(page_num) + '_p/'
    
    try:
        url_data  = urllib2.urlopen(url_name)
        soup      = BeautifulSoup(url_data)
        houses    = soup.findAll('article')
    except:
        print('\nPROBLEM WITH ZIP CODE: ' + str(z_code))
        return
    
    # iterate through pages
    
    while len(houses)!=0:
        
        # iterate through house listings
        
        print url_name
        
        for ihouse in houses:
            parse_somestuff(ihouse)
        
        page_num+=1 # advance page
        sleep(randint(500,1000)/100)
        url_name  = base_url + str(page_num) + '_p/' 
        url_data  = urllib2.urlopen(url_name)
        soup      = BeautifulSoup(url_data)
        houses    = soup.findAll('article')
        
        session.commit()
        
        
# specify method to call sql

engine = create_engine('mysql+pymysql://root@127.0.0.1/housedb', pool_recycle=5, echo=False)

# setup schema

Base = declarative_base()

class House(Base):
    __tablename__ = 'housedb2'

    id      = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    houseid = Column(Integer)
    price   = Column(Integer)
    address = Column(String(100))
    h_lot   = Column(Integer)
    h_lat   = Column(Float)
    h_long  = Column(Float)
    h_date  = Column(Date)
    h_room  = Column(Integer)
    h_sqft  = Column(Integer)
    h_zip   = Column(Integer)

    # spit out the entry if asked 
    def __repr__(self):
        return ("<HOUSE:(\n\thouseid  = '%d'\n\tprice = '%d'\n\taddress  = '%s' \
        \n\th_lot   = '%d'\n\th_lat  = '%.4f'\n\th_long  = '%.4f' \n\th_date  = '%s'\
        \n\th_room   = '%d'\n\th_sqft   = '%d' \n\th_zip   = '%d')>" % (self.houseid,
        self.price,self.address,self.h_lot,self.h_lat,self.h_long,self.h_date,
        self.h_room,self.h_sqft,self.h_zip)) 
        
# create that table!
        
Base.metadata.create_all(engine)

# create a session to talk to SQL

Session = sessionmaker(bind=engine)
session = Session()

# start your engines

def cycle_through():
    global zip_code
    for z_code in zip_code:
        sleep(randint(1000,3000)/1000)
        process_code(z_code)   
        
def main():
    cycle_through()
    
if __name__ == "__main__":
    main()
    