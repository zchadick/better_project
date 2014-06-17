# what do you need?

from bs4         import BeautifulSoup
from sf_zipcodes import zip_code
from random      import randint
from time        import sleep
import urllib2
import re
import string


# find the maximum number of pages available for given zip code

def find_max_pages(soup):
    str_trsh = str(soup)
    s_flag   = 1
    max_page = [1]
    
    while s_flag:
        ind = str_trsh.find('changePage')
        
        if ind==-1:
            max_page = max(max_page)
            s_flag   = 0
        else:
            max_page.append(int(re.findall(r'\d+',str_trsh[ind+10:ind+15])[0]))
            str_trsh = str_trsh[ind+10:]
    
    return max_page

# parse through individual houses

def parse_somestuff(ihouse):

    #ihouse  = houses[0]
    hparsed = str(ihouse)
    
    # get address information
    
    address = ihouse.find('span',{'itemprop':'streetAddress'}).string
    
    # get zipcode information
    
    zipcode = int(ihouse.find('span',{'itemprop':'postalCode'}).string)
    
    # get size of lot
    
    lot_s   = ihouse.find('dt',{'class':'property-lot'}).string
    lot_s   = int(string.join(re.findall(r'\d+',lot_s)).replace(' ',''))
    
    # get latitude of house
    
    h_lat   = ihouse.find('meta',{'itemprop':'latitude'})
    h_lat   = float(h_lat['content'])
    
    # get longitude of house
    
    h_long  = ihouse.find('meta',{'itemprop':'longitude'})
    h_long  = float(h_long['content'])
    
    # get and parse sale date
    
    temp_d  = ihouse.find('dt',{'class':'sold-date'}).string
    temp_d  = re.findall(r'\d+',temp_d)
    
    new_d   = []
    for dates in temp_d:
        new_d.append(int(dates))
    
    sale_d  = str(new_d[2]%2000+2000) + '-' + str(new_d[0]).zfill(2) + '-' + str(new_d[2]).zfill(2)
    
    # get and parse house properties (sqft and bedrooms)
    
    temp_d  = str(ihouse.find('dt',{'class':'property-data'}))
    temp_d  = re.findall(r'\d+',str(temp_d).replace(',',''))
    
    bed_d   = int(temp_d[0])
    sqft_d  = int(temp_d[-1])
    
    # get zillow ID 
    
    id_ind  = hparsed.find('id=')
    id_d    = int(hparsed[id_ind+9:id_ind+17])
    
    # get and parse sale price
    
    s_ind   = hparsed.find('Sold:')
    p_temp  = hparsed[s_ind+6:]
    s_end   = p_temp.find('<')
    t_price = p_temp[:s_end]
    price_s = string.join(re.findall(r'[-+]?\d*\.\d+|\d+',t_price)).replace(' ','')
    
    price   = float(price_s)
    
    if t_price[-1]=='M':   
        price = price*1000000    
    elif t_price[-1]=='K':
        price = t_price*1000 
        
    price   = int(round(price))
    
    # print some shit
    
    print ('\n\nNEW HOUSE\n\n')
    print ('price     ' + str(price))
    print ('address   ' + str(address))
    print ('zipcode   ' + str(zipcode))
    print ('lot size  ' + str(lot_s))
    print ('latitude  ' + str(h_lat))
    print ('longitude ' + str(h_long))
    print ('sale date ' + str(sale_d))
    print ('# of room ' + str(bed_d))
    print ('SQFT      ' + str(sqft_d))
    print ('ID        ' + str(id_d))
    
# process a single zip code

def process_code(z_code):
    page_num  = 1
    base_url  = 'http://www.zillow.com/san-francisco-ca-' + str(z_code) + '/sold/'
    url_name  = base_url + str(page_num) + '_p/'
    
    try:
        url_data  = urllib2.urlopen(url_name)
        soup      = BeautifulSoup(url_data)
        houses    = soup.findAll('article')
    except:
        print('\nPROBLEM WITH ZIP CODE: ' + str(z_code))
        return
    
    max_page  = find_max_pages(soup)
    
    # iterate through pages
    
    while page_num<=max_page:
        sleep(randint(50,100)/10)
        url_name  = base_url + str(page_num) + '_p/' 
        url_data  = urllib2.urlopen(url_name)
        soup      = BeautifulSoup(url_data)
        houses    = soup.findAll('article')
        
        # iterate through house listings
        
        for ihouse in houses:
            parse_somestuff(ihouse)
        
        page_num+=1 # advance page
        print url_name
        
        
for z_code in zip_code:
    sleep(randint(50,100)/10)
    process_code(z_code)