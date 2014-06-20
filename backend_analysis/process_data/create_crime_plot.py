#! /usr/bin/python

import pymysql
import matplotlib
import math
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta

db_name    = 'citydata'
table_name = 'crimedata'
place_id   = 9999

# get column names

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db=db_name)
cur  = conn.cursor()

sql_query = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE \
            TABLE_SCHEMA='{0}' AND TABLE_NAME='{1}';".format(db_name,table_name)

cur.execute(sql_query)
data  = cur.fetchall()

d_labels = list(data[2:-1])
n_labels = []

for text in d_labels:
	xx = text[0]
	n_labels.append('-'.join([xx[1:5],xx[5:7]]))

# get data

sql_query = 'SELECT * FROM {0} WHERE place_id = {1};'.format(table_name,place_id)
cur.execute(sql_query)
data  = cur.fetchall()
cur.close()
conn.close()

data  = list(data[0][2:-1])
x_dat = range(1,len(data)+1)

fig, ax = plt.subplots()
plt.plot(x_dat,data)
plt.title('CRIME NUMBERS FOR ALL OF SAN FRANCISCO')
plt.xlabel('DATE')
plt.xticks(x_dat[0::12])
ax.set_xticklabels(n_labels[0::12])
plt.ylabel('# of CRIMES')
plt.grid(True)
plt.figtext(0.995, 0.01, 'crimespotting.org',ha='right', va='bottom')
plt.tight_layout(pad=1) 
plt.savefig('/Users/chadick/Desktop/filename.png')
plt.close()

