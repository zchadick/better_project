import pymysql
import math

from app       import app
from operator  import itemgetter

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

    cur.close()
    conn.close()

    return {'ind':ind,'db_id':db_id,'db_name':db_name,'db_lat':db_lat,'db_lon':db_lon}