# this guy gets the data to fill it for the heatmap overlays

import pymysql
import datetime

from dateutil.relativedelta import relativedelta
from app                    import app

def get_heatmap_points(hm_type,hm_year,hm_month):
    db_host = app.config['DATABASE_HOST']
    db_port = app.config['DATABASE_PORT']
    db_user = app.config['DATABASE_USER']
    db_pass = app.config['DATABASE_PASSWORD']
    
    heat_data  = []

    date_start = datetime.date(int(hm_year),int(hm_month),1)
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
        cur.close()
        conn.close()
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

    cur.close()
    conn.close()

    return heat_data