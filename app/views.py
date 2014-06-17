from flask import render_template, _app_ctx_stack, jsonify, request
from app import app, host, port, user, passwd, db
from app.helpers.database import con_db
from operator import itemgetter

#import numpy as np
#import matplotlib.pyplot as plt
#import MySQLdb
import pymysql
import sys
import simplejson
import urllib2
import json
import math


# To create a database connection, add the following
# within your view functions:
# con = con_db(host, port, user, passwd, db)

#from app.helpers.database import con_db, query_db
#from app.helpers.filters import format_currency
import jinja2
 
#def get_db():
#	print "Getting DB"
#	top = _app_ctx_stack.top
#	if not hasattr(top, 'home_kitchen_db'):
#		top.home_kitchen_db = pymysql.connect(host="localhost", user="root", db = "semfundc_zidisha")
#	return top.home_kitchen_db
#
#def query_db(query):
#	sys.stderr.write("Querying Database with: "  + query)
#	cursor = get_db().cursor()
#	cursor.execute(query)
#	return cursor.fetchall()
#
#def running_average(data):
#	result = []
#	index = 0
#	total = 0
#	for x in data:
#		index += 1
#		total += x[1]
#		result.append([x[0], total/index])
#	return result	

@app.route('/')
def index():
	return render_template('index.html')

#@app.route('/product/json/<product_id>')
#def product_details(product_id):
#        address = product_id
#        
#        # need to add some error checking here
#        
#        address = address.replace(' ','+')
#        address = address + ',+San+Francisco,+CA'
#        
#            
#        url_name = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + address + '&key=AIzaSyClGti21OO4dZ1P-BbQGr-Jezy2qV8zajg'
#        url_data = urllib2.urlopen(url_name)
#        
#        json_string = url_data.read()
#        parsed_json = json.loads(json_string)
#        
#        data = parsed_json['results'][0]
#        data = data.get('geometry')
#        data = data.get('location')
#        lat  = data.get('lat')
#        lng  = data.get('lng')
#        
#        return('YOU ENTERED AN ADDRESS AT %.4f and %.4f\n' % (lat,lng))
        
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
        clo_name = dat.get('clo_name')
        clo_vals = dat.get('clo_vals')

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

        out_text = ('closest point was in the {0} with value of {1}'.format(clo_name,clo_vals))
        
        return render_template('index.html',t_dat = t_text,la_data = la_data, lo_data = lo_data, valid = valid, out_text = out_text)
        
        
	#data = query_db(query)
	#data = running_average(data)
	#formatted_data = map(lambda d: {'time': d[0], 'rating':d[1]}, data)
	#return jsonify(reviews = formatted_data)
	
def parse_the_location(p_lat,p_lon):
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='website_test')
    cur  = conn.cursor()
    cur.execute("SELECT * FROM webtest")
    data  = cur.fetchall()

    test1 = []
    test2 = []
    test3 = []
    test4 = []
    test5 = []

    for r in data:
        test1.append(r[0])
        test2.append(r[1])
        test3.append(r[2])
        test4.append(r[3])
        test5.append(r[4])

    p_dist = []

    for x in range(0,len(test1)):
        p_dist.append(math.sqrt(math.pow(test3[x]-p_lat,2)+math.pow(test4[x]-p_lon,2)))

    ind = min(enumerate(p_dist), key=itemgetter(1))[0]

    clo_name = test2[ind]
    clo_vals = test5[ind]

    return {'clo_name':clo_name, 'clo_vals':clo_vals}
        



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

