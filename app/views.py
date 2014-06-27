from flask                  import render_template, _app_ctx_stack, jsonify, request, send_file
from app                    import app, host, port, user, passwd, db
from app.helpers.database   import con_db

# fix these guys... must be a quick fix

from get_heatmap_points     import get_heatmap_points
from check_in_city          import check_in_city
from get_point_data         import get_point_data
from parse_the_location     import parse_the_location
from graph_the_data         import graph_the_data

import urllib2
import json

# render initial template

@app.route('/')
def index():
    citycheck = check_in_city(1,1)
    sfpoints  = citycheck.get('sfpoints')
    return render_template('index.html',ind=9999,sfpoints = sfpoints)
      
# render the page after you've added in some search data

@app.route('/out', methods=['POST'])
def out():
    valid     = False
    plot_heat = False

    address   = request.form['searchPhrase']
    hm_type   = request.form['inlineRadioOptions']
    month_in  = request.form['dd_month']
    year_in   = request.form['dd_year']

    # search for the address location

    address   = address.replace(' ','+')
    address   = address + ',+San+Francisco,+CA'
      
    url_name  = 'https://maps.googleapis.com/maps/api/geocode/json?address=' \
                + address + '&key=AIzaSyClGti21OO4dZ1P-BbQGr-Jezy2qV8zajg'
    url_data  = urllib2.urlopen(url_name)

    json_string = url_data.read()
    parsed_json = json.loads(json_string)

    data = parsed_json['results'][0]
    data = data.get('geometry')
    data = data.get('location')
    lat  = data.get('lat')
    lng  = data.get('lng')

    citycheck = check_in_city(lat,lng)
    sfpoints  = citycheck.get('sfpoints') # outline of the city
    
    if citycheck.get('notincity') == 1: # check if lat/lng location is within SF
        return render_template('index.html',ind      = 9999,
                                            t_dat    = 'ADDRESS OUTSIDE OF SAN FRANCISCO',
                                            sfpoints = sfpoints)

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

    # generate heat-map data (if requested)

    if hm_type!='none' and year_in!=99 and month_in!=99:
        heat_data = get_heatmap_points(hm_type,int(year_in),int(month_in))
    else:
        heat_data = []

    if len(heat_data)!=0:
        plot_heat = True

    # format prediction screen

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

    # send a bunch of stuff to html... prolly better way to do this...

    return render_template('index.html',t_dat     = t_text,    la_data  = la_data,  lo_data   = lo_data, 
                                        valid     = valid,     out_text = out_text, db_id     = db_id,
                                        db_name   = db_name,   db_lat   = db_lat,   db_lon    = db_lon,
                                        ind       = ind,       vals     = vals,     civ       = civ,
                                        zid       = zid,       z_str    = z_str,    heat_data = heat_data,
                                        plot_heat = plot_heat, sfpoints = sfpoints)

@app.route('/plot.png')
def getPlot():
    id_dat = request.args.get('id_num')
    img    = graph_the_data(id_dat)
    return send_file(img, mimetype='image/png')  

@app.route('/slides')
def about():
    return render_template('slides.html')

@app.route('/author')
def contact():
    return render_template('author.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.route('/<pagename>')
def regularpage(pagename=None):
    return "You've arrived at " + pagename + " ... have you considered NOT typing a 'special' page?"

@app.route('/robots.txt')
def static_from_root():
      return send_from_directory(app.static_folder, request.path[1:])