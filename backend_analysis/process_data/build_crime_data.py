#! /usr/bin/python

import pymysql
import matplotlib.path
import sqlalchemy
import math
import datetime
import numpy as np

from sqlalchemy                 import create_engine, Sequence
from sqlalchemy                 import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types           import Float, Date
from sqlalchemy.orm             import sessionmaker
from dateutil.relativedelta     import relativedelta


table_name = 'pricedata'

def get_spacing_information():
    # connect to the database to get how far apart 'points' are
    conn  = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='citydata')
    cur   = conn.cursor()
    cur.execute("SELECT latitude,longitude FROM citypoints LIMIT 2;")
    data  = cur.fetchall()
    conn.close()

    spacing = max(abs(data[0][1]-data[1][1]),(data[0][0]-data[1][0]))
    return spacing

def get_timestamps():
    # connect to the database and get listing of times
    conn  = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='housedb')
    cur   = conn.cursor()
    cur.execute("SELECT DISTINCT h_date from housedb3;")
    data  = cur.fetchall()
    conn.close()

    dates = sorted(data,key = lambda x: x[0])
    return dates

def cycle_through_times(dates,spacing,sql_str1,lat,lon,place_id):
    # connect to the database and start querying

    conn   = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='housedb')
    cur    = conn.cursor()
    p_data = []

    for row in dates:
        # cycle through all the dates you've found
        date_year  = row[0].year
        date_month = row[0].month
        date_day   = 1
        date_start = datetime.date(date_year,date_month,date_day)
        date_end   = date_start + relativedelta(months=1)
        date_st_s  = str(date_start)
        date_en_s  = str(date_end)
        sql_quer   = "SELECT houseid,price,h_lat,h_long FROM housedb3"  \
                      + " WHERE (h_date>="'"{0}"'" AND h_date<"'"{1}"'") \
                      AND h_room=2;".format(date_st_s,date_en_s)
        cur.execute(sql_quer)
        data = cur.fetchall()

        distance = []
        prices   = []

        for vals in data:
            # cycle through each house listing
            # find the distance to point and impose a gaussian
            dist  = math.sqrt(math.pow(vals[2]-lat,2)+math.pow(vals[3]-lon,2))
            d_val = math.exp(-math.pow(dist,2)/(2*math.pow(spacing/2.3548,2)))

            distance.append(d_val)
            prices.append(d_val*vals[1])

        p_data.append(round(sum(prices)/sum(distance)))

    # connect to SQL database

    cur.close()
    conn.close()

    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='citydata')
    cur  = conn.cursor()

    sql_str1 = sql_str1 + str(place_id) + ','
    for numel in p_data:
        sql_str1 = sql_str1 + str(numel) + ','
    myquery = sql_str1[:-1] + ')'

    print('UPDATING DATABASE FOR PLACE: {0}'.format(place_id))

    cur.execute(myquery)
    conn.commit()  
    cur.close()
    conn.close()

def cycle_through_locations(dates,spacing,sql_str1):
    # connect to the database to get how far apart 'points' are
    conn  = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='citydata')
    cur   = conn.cursor()
    cur.execute("SELECT * FROM citypoints;")
    data  = cur.fetchall()
    cur.close()
    conn.close()

    for num in data:
        cycle_through_times(dates,spacing,sql_str1,num[2],num[3],num[0])

# initial checks

spacing = get_spacing_information()
dates   = get_timestamps()

# create the database table

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='citydata')
cur  = conn.cursor()

create_str = []
name_str   = []
val_str    = []
write_str  = []

create_str.append('CREATE TABLE {0} (id INTEGER PRIMARY KEY AUTO_INCREMENT UNIQUE NOT NULL'.format(table_name))
create_str.append('place_id INTEGER')

for d_dat in dates:
    date_year  = d_dat[0].year
    date_month = d_dat[0].month
    date_day   = 1
    date_start = datetime.date(date_year,date_month,date_day)

    date_str = 'd'+str(date_start).replace('-','')+'d'
    write_str.append(date_str)
    val_str.append('%f')
    create_str.append(date_str + ' FLOAT')

create_str = ','.join(create_str)
create_str = create_str + ')'

sql_str1 = []
sql_str1.append('INSERT INTO {0} (place_id,'.format(table_name))
write_str = ','.join(write_str)
sql_str1.append(write_str)
sql_str1.append(') VALUES (')
sql_str1 = ' '.join(sql_str1)


drop_str = 'DROP TABLE IF EXISTS {0}'.format(table_name)
#cur.execute(drop_str)
cur.execute(create_str)
conn.commit()  
cur.close()
conn.close()

# cycle through all locations

cycle_through_locations(dates,spacing,sql_str1)

# get the city-wide averages

print('UPDATING DATABASE FOR ENTIRE CITY')

p_data = []
s_data = []

for row in dates:
    # cycle through all the dates you've found

    conn   = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='housedb')
    cur    = conn.cursor()

    date_year  = row[0].year
    date_month = row[0].month
    date_day   = 1
    date_start = datetime.date(date_year,date_month,date_day)
    date_end   = date_start + relativedelta(months=1)
    date_st_s  = str(date_start)
    date_en_s  = str(date_end)
    sql_quer   = "SELECT price FROM housedb3"  \
                  + " WHERE (h_date>="'"{0}"'" AND h_date<"'"{1}"'") \
                  AND h_room=2;".format(date_st_s,date_en_s)

    cur.execute(sql_quer)
    data = cur.fetchall()
    p_data.append(np.mean(data))
    s_data.append(np.std(data))

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='citydata')
cur  = conn.cursor()

str_copy = sql_str1

sql_str1 = str_copy
sql_str1 = sql_str1 + str(9998) + ','
for numel in p_data:
    sql_str1 = sql_str1 + str(numel) + ','
myquery = sql_str1[:-1] + ')'

cur.execute(myquery)
conn.commit()  

sql_str1 = str_copy
sql_str1 = sql_str1 + str(9999) + ','
for numel in s_data:
    sql_str1 = sql_str1 + str(numel) + ','
myquery = sql_str1[:-1] + ')'

cur.execute(myquery)
conn.commit()  
cur.close()
conn.close()

print('DONE!')