from flask                  import render_template, _app_ctx_stack, jsonify, request, send_file
from app                    import app, host, port, user, passwd, db
from app.helpers.database   import con_db
from operator               import itemgetter
from StringIO               import StringIO
from dateutil.relativedelta import relativedelta


import pymysql
import sys
import simplejson
import urllib2
import json
import math
import jinja2
import matplotlib
import math
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

@app.route('/')
def index():
	return render_template('index.html',ind=9999)
        
@app.route('/out', methods=['POST'])

def out():
    valid = 'False'

    address = request.form['searchPhrase']
            
    # need to add some error checking here

    address = address.replace(' ','+')
    address = address + ',+San+Francisco,+CA'

        
    url_name = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + address + '&key=AIzaSyClGti21OO4dZ1P-BbQGr-Jezy2qV8zajg'
    url_data = urllib2.urlopen(url_name)

    json_string = url_data.read()
    parsed_json = json.loads(json_string)

    data = parsed_json['results'][0]
    data = data.get('geometry')
    data = data.get('location')
    lat  = data.get('lat')
    lng  = data.get('lng')

    dat      = parse_the_location(lat,lng)
    db_id    = dat.get('db_id')
    db_name  = dat.get('db_name')
    db_lat   = dat.get('db_lat')
    db_lon   = dat.get('db_lon')
    ind      = dat.get('ind')
    clo_name = db_name[ind]
    clo_vals = db_id[ind]
    clo_lat  = db_lat[ind]
    clo_lon  = db_lon[ind]

    if ((37.7651185 > lat > 37.7529621) & (-122.4176042 < lng < -122.4066062)): 
        t_text  = ('GOOD: YOU ENTERED AN ADDRESS AT %.4f and %.4f\n VALUE WILL GO UP $1243 IN 3 MONTHS \n' % (lat,lng))
        la_data = lat
        lo_data = lng 
        valid   = True
    else:
        t_text  = ('BAD: YOU ENTERED AN ADDRESS AT %.4f and %.4f\n' % (lat,lng))
        la_data = lat
        lo_data = lng
        valid   = True

    out_text = ('closest point was {0} <br> with value of {1}'.format(clo_name,clo_vals))

    return render_template('index.html',t_dat   = t_text,  la_data  = la_data,  lo_data = lo_data, 
                                        valid   = valid,   out_text = out_text, db_id   = db_id,
                                        db_name = db_name, db_lat   = db_lat,   db_lon  = db_lon,
                                        ind     = ind)
	
def parse_the_location(p_lat,p_lon):
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='citydata')
    cur  = conn.cursor()
    cur.execute("SELECT * FROM citypoints")
    data  = cur.fetchall()

    db_id   = []
    db_name = []
    db_lat  = []
    db_lon  = []

    for r in data:
        db_id.append(r[0])
        db_name.append(r[1])
        db_lat.append(r[2])
        db_lon.append(r[3])

    p_dist = []

    for x in range(0,len(db_id)):
        p_dist.append(math.sqrt(math.pow(db_lat[x]-p_lat,2)+math.pow(db_lon[x]-p_lon,2)))

    ind = min(enumerate(p_dist), key=itemgetter(1))[0]

    return {'ind':ind,'db_id':db_id,'db_name':db_name,'db_lat':db_lat,'db_lon':db_lon}
        
@app.route('/plot.png')
def getPlot():

    id         = request.args.get('id_num')
    db_name    = 'citydata'
    table_name = 'crimedata'
    place_id   = id

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

    db_name    = 'citydata'
    table_name = 'pricedata'
    place_id   = id

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

    if str(place_id)==str(9999):
        p_title = 'AVERAGE SALE PRICE FOR ALL OF SAN FRANCISCO'
    else:
        p_title = 'AVERAGE SALE PRICE FOR LOCAL NEIGHBORHOOD'

    print n_labels

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
    return send_file(img, mimetype='image/png')

@app.route('/home')
def home():
    # Renders home.html.
    return render_template('home.html')

@app.route('/slides')
def about():
    # Renders slides.html.
    return render_template('slides.html')

@app.route('/author')
def contact():
    # Renders author.html.
    return render_template('author.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.route('/<pagename>')
def regularpage(pagename=None):
    # Renders author.html.
    return "You've arrived at " + pagename

