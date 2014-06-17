import pymysql

crime_sql = 'crimedb'
host_sql  = '127.0.0.1'

conn = pymysql.connect(host=host_sql, port=3306, user='root', passwd='', db=crime_sql)
cur  = conn.cursor()
cur.execute("SELECT DISTINCT typecr FROM crimedb1;")
data  = cur.fetchall()