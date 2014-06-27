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

matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.path

@app.route('/')
def index():
	return render_template('index.html',ind=9999)
        
@app.route('/out', methods=['POST'])
def out():
    valid     = False
    plot_heat = False

    address   = request.form['searchPhrase']
    button_v  = request.form['inlineRadioOptions']
    month_in  = request.form['dd_month']
    year_in   = request.form['dd_year']

    print address
            
    # need to add some error checking here

    address   = address.replace(' ','+')
    address   = address + ',+San+Francisco,+CA'
      
    url_name  = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + address + '&key=AIzaSyClGti21OO4dZ1P-BbQGr-Jezy2qV8zajg'
    url_data  = urllib2.urlopen(url_name)

    json_string = url_data.read()
    parsed_json = json.loads(json_string)

    data = parsed_json['results'][0]
    data = data.get('geometry')
    data = data.get('location')
    lat  = data.get('lat')
    lng  = data.get('lng')

    notincity = check_in_city(lat,lng)
    if notincity == 1:
        return render_template('index.html',ind=9999, t_dat = 'ADDRESS OUTSIDE OF SAN FRANCISCO')

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

    heat_data = get_heatmap_points('cityprice',[2014,3])

    if len(heat_data)!=0:
        plot_heat = True

    if ind!=9999: 
        l_data   = get_point_data(ind)
        vals     = l_data.get('val')
        civ      = l_data.get('civ')
        zid      = l_data.get('zid')
        la_data  = lat
        lo_data  = lng
        valid    = True
        t_text   = 'VALUE WILL CHANGE ${0} IN 3 MONTHS ({1}%)'.format(vals,civ)
        out_text = t_text
        z_str    = "static/pot{0}.png".format(zid)
    else:
        t_text   = ('BAD: CANNOT PARSE THIS!')
        la_data  = lat
        lo_data  = lng
        out_text = t_text

    return render_template('index.html',t_dat     = t_text,    la_data  = la_data,  lo_data   = lo_data, 
                                        valid     = valid,     out_text = out_text, db_id     = db_id,
                                        db_name   = db_name,   db_lat   = db_lat,   db_lon    = db_lon,
                                        ind       = ind,       vals     = vals,     civ       = civ,
                                        zid       = zid,       z_str    = z_str,    heat_data = heat_data,
                                        plot_heat = plot_heat)
def get_point_data(ind):
    db_host = app.config['DATABASE_HOST']
    db_port = app.config['DATABASE_PORT']
    db_user = app.config['DATABASE_USER']
    db_pass = app.config['DATABASE_PASSWORD']
    db_name = app.config['DATABASE_DB']
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user, passwd=db_pass, db=db_name)
    cur  = conn.cursor()
    cur.execute('SELECT * FROM pricecrime WHERE zip_id={0}'.format(ind))
    data  = cur.fetchall()

    val = data[0][2]
    civ = data[0][3]
    zid = data[0][4]

    return {'val':val,'civ':civ,'zid':zid}

def parse_the_location(p_lat,p_lon):
    db_host = app.config['DATABASE_HOST']
    db_port = app.config['DATABASE_PORT']
    db_user = app.config['DATABASE_USER']
    db_pass = app.config['DATABASE_PASSWORD']
    db_name = app.config['DATABASE_DB']
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user, passwd=db_pass, db=db_name)
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

def check_in_city(lat,lng):
    sf = [[37.809812,-122.476634],
          [37.797346,-122.481910],
          [37.788471,-122.490044],
          [37.786681,-122.496047],
          [37.787849,-122.502443], 
          [37.785374,-122.510171],
          [37.780344,-122.514118],
          [37.772203,-122.514577], 
          [37.708283,-122.503009],
          [37.707944,-122.391354],
          [37.708315,-122.380821], 
          [37.716061,-122.375920], 
          [37.715668,-122.365390],
          [37.728642,-122.358034],
          [37.739688,-122.368804], 
          [37.753637,-122.378594], 
          [37.788308,-122.387641],
          [37.807490,-122.404791],
          [37.810019,-122.415333], 
          [37.804758,-122.462631], 
          [37.807265,-122.468261]]

    shape = matplotlib.path.Path(sf)
    if shape.contains_point([lat,lng]):
        notincity = 0
    else:
        notincity = 1
    return notincity

def get_heatmap_points(hm_type,hm_date):
    db_host = app.config['DATABASE_HOST']
    db_port = app.config['DATABASE_PORT']
    db_user = app.config['DATABASE_USER']
    db_pass = app.config['DATABASE_PASSWORD']
    
    heat_data  = []

    date_start = datetime.date(hm_date[0],hm_date[1],1)
    date_end   = date_start + relativedelta(months=1)
    date_st_s  = str(date_start)
    date_en_s  = str(date_end)
    date_str   = 'd'+str(date_start).replace('-','')+'d'
    
    if hm_type == 'crimedb':
        db_name  = 'crimedb'
        sql_quer = "SELECT typecr, latcr, loncr FROM crimedb1  " \
                     + "WHERE (datecr>="'"{0}"'" AND datecr<"'"{1}"'");".format(date_st_s,date_en_s)
    elif hm_type == 'housedb':
        db_name  = 'housedb'
        sql_quer = "SELECT price,h_lat,h_long FROM housedb3 " \
                     + "WHERE (h_date>="'"{0}"'" AND h_date<"'"{1}"'") AND h_room=2;".format(date_st_s,date_en_s)
    elif hm_type == 'pricecrime':
        db_name  = 'citydata'
        sql_quer = "SELECT ZVAL FROM pricecrime WHERE (zip_id<9998);"
    elif hm_type == 'cityprice':
        db_name  = 'citydata'
        sql_quer = "SELECT {0} FROM pricedata WHERE (place_id<9998);".format(date_str)
    elif hm_type == 'citycrime':
        db_name  = 'citydata'
        sql_quer = "SELECT {0} FROM crimedata WHERE (place_id<9998);".format(date_str)
    else:
        return heat_data

    conn = pymysql.connect(host=db_host, port=db_port, user=db_user, passwd=db_pass, db=db_name)
    cur  = conn.cursor()
    cur.execute(sql_quer)
    data = cur.fetchall()

    if db_name == 'citydata':
        sql_quer = "SELECT latitude,longitude FROM citypoints;"
        conn = pymysql.connect(host=db_host, port=db_port, user=db_user, passwd=db_pass, db=db_name)
        cur  = conn.cursor()
        cur.execute(sql_quer)
        ldat = cur.fetchall()

    for ind in range(0,len(data)):
        if hm_type == 'crimedb':
            if data[ind][0] in ['SIMPLE ASSAULT','ROBBERY','AGGRAVATED ASSAULT','ARSON']:
                heat_data.append([data[ind][1],data[ind][2],10])
            else:
                heat_data.append([data[ind][1],data[ind][2],1])
        elif hm_type == 'housedb':
            heat_data.append([data[ind][1],data[ind][2],data[ind][0]])
        else:
            heat_data.append([ldat[ind][0],ldat[ind][1],data[ind][0]])

    return heat_data
        
@app.route('/plot.png')
def getPlot():

    id         = request.args.get('id_num')
    table_name = 'crimedata'
    place_id   = id

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
    place_id   = id

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

@app.route('/robots.txt')
def static_from_root():
      return send_from_directory(app.static_folder, request.path[1:])