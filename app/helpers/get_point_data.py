import pymysql
from app import app

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

    cur.close()
    conn.close()

    return {'val':val,'civ':civ,'zid':zid}