#!/usr/bin/python

import sys
import os
import urllib

sys.path.append('/petabox/sw/lib/python')
sys.path.append(os.path.expanduser("~") + '/openlibrary')

from openlibrary.api import OpenLibrary
import simplejson as json
from lxml import etree

# get_url()
#______________________________________________________________________________
def get_url(url):
    f = urllib.urlopen(url)    
    c = f.read()
    f.close()
    return c

# get_ol_record()
#______________________________________________________________________________
def get_ol_record(iaid):
    url = 'http://openlibrary.org/ia/'+iaid+'.json'
    c = get_url(url)
    
    oljson = json.loads(c)
    olkey = oljson['key']
    
    return olkey, oljson
    

# has_toc()
#______________________________________________________________________________
def has_toc(oljson):
    if 'table_of_contents' in oljson:
        return True
    else:
        return False

# get_item_loc()
#______________________________________________________________________________
def get_item_loc(iaid):
    url = 'http://www.archive.org/services/find_file.php?file=%s&loconly=1' % (iaid)
    c = get_url(url)
    
    tree = etree.fromstring(c)
    loc = tree.find('.//location')
    host = loc.get('host')
    dir  = loc.get('dir')
    return host, dir
    

# get_toc()
#______________________________________________________________________________
def get_toc(iaid):

    host, dir = get_item_loc(iaid)
    
    url = 'http://%s/~mccabe/BookReader/BookReaderGetTocWrapper.php?item_id=%s&doc=%s&path=%s' % (host, iaid, iaid, dir)
    print 'toc url is ' + url
    c = get_url(url)
    
    print 'got toc string: ' + c

    toc = json.loads(c)
    return toc    
    
# add_toc_to_json()
#______________________________________________________________________________
def add_toc_to_json(oljson, toc):
    def addkey(o):
        o["type"] = {"key": "/type/toc_item"}
        o["pagenum"] = str(o["pagenum"])
        return o
    newtoc = [addkey(toc_item) for toc_item in toc]
    
    oljson['table_of_contents'] = newtoc

    print json.dumps(oljson, indent=4)

    return oljson

# write_to_ol()
#______________________________________________________________________________
def write_to_ol(olkey, oljson):

    ol = OpenLibrary("http://openlibrary.org")

    # Log in [daniel, sam]
    logged_in = False
    for attempt in range(5):
        try:
            ol.autologin()
            logged_in = True
            break
        except:
            print 'ol.autologin() error; retrying'
    if not logged_in:
        sys.exit('Failed to log in.')    

    ol.save(olkey, oljson, 'Adding Table of Contents')

    
# __main()__
#______________________________________________________________________________

iaid = 'logofcowboynarra00adamuoft'
#iaid = 'flatlandromanceo00abbouoft'

olkey, oljson = get_ol_record(iaid)

#print 'got ol record for key=%s: %s' % (olkey, oljson)

if has_toc(oljson):
    sys.exit('this record already has a Table of Contents!')
    
toc = get_toc(iaid)

if not toc:
    sys.exit('could not generate TOC for this book!')    

newjson = add_toc_to_json(oljson, toc)

write_to_ol(olkey, newjson)
