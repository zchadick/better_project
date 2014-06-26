# this creates a database of lat-lon pairs bounded by 
# san francisco boarders (using number_points)

import matplotlib.path
import sqlalchemy
import numpy as np

from get_sf_borders             import sf
from sqlalchemy                 import create_engine, Sequence
from sqlalchemy                 import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types           import Float, Date
from sqlalchemy.orm             import sessionmaker

number_points = 100 # approximate number of points to overlay on the city

def filter_places(places,sf):
     # filter out those places which are out-o-bounds
     shape      = matplotlib.path.Path(sf)        
     new_places =[]

     for row in places:
          if shape.contains_point(row):
               new_places.append(row)

     return new_places

def create_points(min_lat,max_lat,min_lon,max_lon,spacing):
     # create a set of point to fullfill the prophecy!
     lat_list = np.arange(min_lat+spacing,max_lat-spacing,spacing)
     lon_list = np.arange(min_lon+spacing,max_lon-spacing,spacing)

     places   = []

     for rlat in lat_list:
          for rlon in lon_list:
               places.append([rlat,rlon])
     return places

def adjust_spacing(places,spacing,number_points):
     # adjust spacing
     if len(places)<number_points:
          spacing = spacing*0.95
     else:
          spacing = spacing*1.05
     return spacing

# calculate limits on SF boundries

lat = []
lon = []

for row in sf:
     lat.append(row[0])
     lon.append(row[1])

min_lat = min(lat)
max_lat = max(lat)
min_lon = min(lon)
max_lon = max(lon)

# calculate inital spacing information and pupulate 

lat_span = max_lat - min_lat
lon_span = max_lon - min_lon
spacing  = np.sqrt(lat_span*lon_span/number_points)
places   = create_points(min_lat,max_lat,min_lon,max_lon,spacing)
places   = filter_places(places,sf)

# there were some "bounding effects" so adjust min/max's

min_lat = min_lat-spacing
max_lat = max_lat+spacing
min_lon = min_lon-spacing
max_lon = max_lon+spacing

# iterate a solution!

iter_num = 1

while ((len(places)!=number_points) & (iter_num<500)):
     spacing   = adjust_spacing(places,spacing,number_points)
     places    = create_points(min_lat,max_lat,min_lon,max_lon,spacing)
     places    = filter_places(places,sf)
     iter_num += 1

# create a SQL instance to hold this information

engine = create_engine('mysql+pymysql://root@127.0.0.1/citydata', pool_recycle=5, echo=False)
Base   = declarative_base()

# create schema to hold on to data

class CPOINT(Base):
    __tablename__ = 'citypoints'

    id        = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name      = Column(String(25))
    latitude  = Column(Float)
    longitude = Column(Float)


    # spit out the entry if asked 
    def __repr__(self):
        return ("<CPOINT:(\n\tname      = '%s'\n\tlatitude  = '%.4f' \
        \n\tlongitude = '%.4f')>" % (self.name,self.latitude,self.longitude)) 

# create that table!
        
Base.metadata.create_all(engine)

# create a session to talk to SQL

Session = sessionmaker(bind=engine)
session = Session()

# add the data to the database

iter_num = 1

for row in places:
     name       = 'point%03d' % iter_num
     place_data = CPOINT(name = name, latitude = float(row[0]),longitude = float(row[1]))
     iter_num  += 1

     session.add(place_data)

session.commit()

print 'SUCCESSFULLY ADDED {0} POINTS TO DATABASE'.format(number_points)