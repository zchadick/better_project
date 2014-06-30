import pymysql
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

from app      import app
from StringIO import StringIO

def graph_the_data(id_dat):
	table_name = 'crimedata'
	place_id   = id_dat

	# get column names

	db_host = app.config['DATABASE_HOST']
	db_port = app.config['DATABASE_PORT']
	db_user = app.config['DATABASE_USER']
	db_pass = app.config['DATABASE_PASSWORD']
	db_name = app.config['DATABASE_DB']
	conn = pymysql.connect(host=db_host, port=db_port, user=db_user, passwd=db_pass, db=db_name)
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

	if str(place_id)==str(9999):
	    p_title = 'CRIME NUMBERS FOR ALL OF SAN FRANCISCO'
	else:
	    p_title = 'CRIME NUMBERS FOR LOCAL NEIGHBORHOOD'

	fig = plt.figure(figsize=(9,12))
	ax1 = fig.add_subplot(2,1,1)
	ax1.plot(x_dat,data)
	ax1.set_title(p_title,size=24)
	ax1.set_xlabel('DATE',size=24)
	ax1.set_xticks(x_dat[0::12])
	ax1.set_xticklabels(n_labels[0::12])
	ax1.set_ylabel('# of CRIMES',size=24)
	ax1.grid(True)
	fig.tight_layout(pad=1) 

	table_name = 'pricedata'
	place_id   = id_dat

	# get column names

	conn = pymysql.connect(host=db_host, port=db_port, user=db_user, passwd=db_pass, db=db_name)
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

	if str(place_id)==str(9999):
	    p_title = 'AVERAGE SALE PRICE FOR ALL OF SAN FRANCISCO'
	else:
	    p_title = 'AVERAGE SALE PRICE FOR LOCAL NEIGHBORHOOD'

	newdata = [x/1000 for x in data]

	ax2 = fig.add_subplot(2,1,2)
	ax2.plot(x_dat,newdata)
	ax2.set_title(p_title,size=24)
	ax2.set_xlabel('DATE',size=24)
	ax2.set_xticks(x_dat[0::12])
	ax2.set_xticklabels(n_labels[0::12])
	ax2.set_ylabel('SALE PRICE ($k)',size=24)
	ax2.grid(True)
	fig.text(0.995, 0.01, 'crimespotting.org and zillow.com',ha='right', va='bottom')
	fig.tight_layout(pad=1) 

	img = StringIO()
	fig.savefig(img)
	img.seek(0)
	return img