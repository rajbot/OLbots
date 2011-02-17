#!/usr/bin/python

# make a text file of library locations suitable for feeding to 
# OpenStreetMaps/OpenLayers: http://wiki.openstreetmap.org/wiki/Openlayers_POI_layer_example

outfile = 'textfile.txt'
import os, codecs
assert not os.path.exists(outfile)
out_fh = codecs.open(outfile, 'w', 'utf-8')

import sys
import urllib
import re

sys.path.append('/petabox/sw/lib/python')
sys.path.append(os.path.expanduser("~") + '/openlibrary')

from openlibrary.api import OpenLibrary
import simplejson as json

name_map = {'boston_public_library': 'BPL',
            'san_francisco_public_library': 'SFPL',
            'university_of_alberta': 'U of Alberta',
            'university_of_florida': 'U of Florida',
            'university_of_toronto': 'U of Toronto',
            }

# get_url()
#______________________________________________________________________________
def get_url(url):
    f = urllib.urlopen(url)    
    c = f.read()
    f.close()
    return c

# get_libraries()
#______________________________________________________________________________
def get_libraries():    
    c = get_url('http://openlibrary.org/libraries')
    
    matches = re.findall('<li><a href="/libraries/(.+)">', c)
    
    return matches

# get_addresses
#______________________________________________________________________________
def get_addresses(library_id):
    url = 'http://openlibrary.org/libraries/'+library_id+'.json'
    c = get_url(url)
    
    oljson = json.loads(c)
    if 'addresses' in oljson:
        addresses = oljson['addresses']
        if isinstance(addresses, dict):                        
            return addresses['value']
        else:
            print "  skipping, not a dict:"
            print "    " + addresses
            return None


    else:
        print '  skipping, no addresses found'
        return None
 

# process_fields(fields)
#______________________________________________________________________________
def process_fields(fields, library_id):
    assert 9 == len(fields)

    branch  = fields[0].strip()
    street  = fields[1].strip()
    city    = fields[2].strip()
    state   = fields[3].strip()
    zip     = fields[4].strip()
    country = fields[5].strip()
    phone   = fields[6].strip()
    link    = fields[7].strip()
    latlong = fields[8].strip().split(',')

    lat	    = latlong[0].strip()
    long    = latlong[1].strip()
    
    if library_id in name_map:
        title = '''<a href="%s">%s - %s</a>'''  % (link, name_map[library_id], branch)
    else:
        title = '''<a href="%s">%s</a>'''  % (link, branch)
        
    desc  = '''%s<br>%s, %s %s  %s<br>%s''' % (street, city, state, zip, country, phone)
    icon  = './img/library.png'
    icon_size = '26x30'
    icon_offset = '-8,-8'
    
    out_fh.write(lat + '\t' + long + '\t' + title + '\t' + desc + '\t' + icon + '\t' + icon_size + '\t' + icon_offset + '\n')
    

# process_addresses
#______________________________________________________________________________
def process_addresses(addresses, library_id):
    for line in addresses.splitlines():
        fields = line.strip().split('|')
        if 9 != len(fields):
            print '  skipping, bad format:'
            print '    ',
            print fields            
        else:
            process_fields(fields, library_id)

# __main()__
#______________________________________________________________________________

out_fh.write('lat\tlon\ttitle\tdescription\ticon\ticonSize\ticonOffset\n')

libraries = get_libraries()

for library_id in libraries:
    print 'processing ' + library_id
    addresses = get_addresses(library_id)
    if addresses:
        process_addresses(addresses, library_id)

out_fh.close()