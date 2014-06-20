# what do you need??

import urllib2
import datetime

# when to start

st_year = 2012
st_mon  = 01
st_day  = 01

# when to end

en_year = 2012
en_mon  = 1
en_day  = 2

count_d = 20 # number of entries to get per query (max 20 for crime-data site)

# parse initial conditions

cur_date   = datetime.date(st_year,st_mon,st_day)
end_date   = datetime.date(en_year,en_mon,en_day)                       
offset     = 0
data       = []

while cur_date!=end_date:

    url_name = 'http://sanfrancisco.crimespotting.org/crime-data?format=csv&count=' \
            + str(count_d) + '&dstart=' + str(cur_date) + '&dend=' + str(cur_date) + '&offset=' + str(offset)

    # parse returned URL data            
                                    
    url_data = urllib2.urlopen(url_name)

    url_text = url_data.read()
    url_list = url_text.split('\n')

    url_list = url_list[1:]

    if url_list[-1]=='':
        url_list = url_list[0:-1]
    
    if len(url_list)!=count_d:
        cur_date += datetime.timedelta(days=1)
        offset    = 0
    else:
        offset += 20
        
    data += url_list

    print(str(cur_date) + '\t' + str(offset))

    
