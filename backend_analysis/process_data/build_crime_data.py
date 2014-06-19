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

table_name = 'crimedata'
bad_crimes = ['SIMPLE ASSAULT','ROBBERY','AGGRAVATED ASSAULT','ARSON']
bc_scale   = 5

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
    conn  = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='crimedb')
    cur   = conn.cursor()
    cur.execute("SELECT DISTINCT datecr from crimedb1;")
    data  = cur.fetchall()
    conn.close()

    t_dates  = sorted(data,key = lambda x: x[0])

    d_start  = t_dates[0][0]
    d_end    = t_dates[-1][0]

    st_year  = d_start.year
    st_month = d_start.month

    en_year  = d_end.year
    en_month = d_end.month

    date_s   = datetime.date(st_year,st_month,1)
    date_e   = datetime.date(en_year,en_month,1)

    dates    = []
    cur_date = date_s
    dates.append(cur_date)

    while cur_date!=date_e:
        cur_date = cur_date + relativedelta(months=1)
        dates.append(cur_date)

    return dates

def cycle_through_times(dates,spacing,sql_str1,lat,lon,place_id,bad_crimes,bc_scale):
    # connect to the database and start querying

    conn   = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='crimedb')
    cur    = conn.cursor()
    p_data = []

    for row in dates:
        # cycle through all the dates you've found
        date_year  = row.year
        date_month = row.month
        date_day   = 1
        date_start = datetime.date(date_year,date_month,date_day)
        date_end   = date_start + relativedelta(months=1)
        date_st_s  = str(date_start)
        date_en_s  = str(date_end)
        sql_quer   = "SELECT typecr, latcr, loncr FROM crimedb1"  \
                      + " WHERE (datecr>="'"{0}"'" AND datecr<"'"{1}"'");".format(date_st_s,date_en_s)
        cur.execute(sql_quer)
        data = cur.fetchall()

        distance = []
        cr_type  = []

        for vals in data:
            # cycle through each crime listing
            # find the distance to point and impose a gaussian
            dist  = math.sqrt(math.pow(vals[1]-lat,2)+math.pow(vals[2]-lon,2))
            d_val = math.exp(-math.pow(dist,2)/(2*math.pow(spacing/2.3548,2)))

            distance.append(d_val)

            if vals[0] in bad_crimes:
                cr_type.append(d_val*bc_scale)
            else:
                cr_type.append(d_val)

        p_data.append(sum(cr_type))

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

def cycle_through_locations(dates,spacing,sql_str1,bad_crimes,bc_scale):
    # connect to the database to get how far apart 'points' are
    conn  = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='citydata')
    cur   = conn.cursor()
    cur.execute("SELECT * FROM citypoints;")
    data  = cur.fetchall()
    cur.close()
    conn.close()

    for num in data:
        cycle_through_times(dates,spacing,sql_str1,num[2],num[3],num[0],bad_crimes,bc_scale)

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
    date_year  = d_dat.year
    date_month = d_dat.month
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

cycle_through_locations(dates,spacing,sql_str1,bad_crimes,bc_scale)

# get the city-wide averages

print('UPDATING DATABASE FOR ENTIRE CITY')

p_data = []
s_data = []

for row in dates:
    # cycle through all the dates you've found

    cr_inds = 0

    conn    = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='crimedb')
    cur     = conn.cursor()

    date_year  = row.year
    date_month = row.month
    date_day   = 1
    date_start = datetime.date(date_year,date_month,date_day)
    date_end   = date_start + relativedelta(months=1)
    date_st_s  = str(date_start)
    date_en_s  = str(date_end)
    sql_quer   = "SELECT typecr FROM crimedb1"  \
                  + " WHERE (datecr>="'"{0}"'" AND datecr<"'"{1}"'");".format(date_st_s,date_en_s)

    cur.execute(sql_quer)
    data = cur.fetchall()

    for ind in data:
        if ind[0] in bad_crimes:
            cr_inds = cr_inds + bc_scale
        else:
            cr_inds = cr_inds + 1

    p_data.append(cr_inds)

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='citydata')
cur  = conn.cursor()

str_copy = sql_str1

sql_str1 = str_copy
sql_str1 = sql_str1 + str(9999) + ','
for numel in p_data:
    sql_str1 = sql_str1 + str(numel) + ','
myquery = sql_str1[:-1] + ')'

cur.execute(myquery)
conn.commit()  
cur.close()
conn.close()

print('DONE!')