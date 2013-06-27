#!/opt/local/Library/Frameworks/Python.framework/Versions/2.7/bin/python
# -*- coding: utf-8 -*-
'''
CRAIGS LIST WEB CRAWLER
'''
import os
import re
import sys
import time
import sqlite3
import urllib
import urllib2
import urlparse
from lxml import etree
from pprint import pprint
from datetime import datetime
from pyquery import PyQuery

#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------

now = datetime.now()

AGENT = 'User-Agent','Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.14) Gecko/20080418 Ubuntu/7.10 (gutsy) Firefox/2.0.0.14'

#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------

class craigsSpider(object):
    # http://austin.craigslist.org/apa/
    
    def __init__(self, db_name, root):
        '''
        CRAIGS LIST WEB-CRAWLER
        @db_name    - name of the database to store scrappings
        @root       - root url from which to begin the scrape
        '''
        self.root      = root
        self.host      = urlparse.urlparse(root)[1]
        
        # connect to DB
        db       = os.path.join(os.getcwd(), db_name)
        self.con = sqlite3.connect(db)
        self.cur = self.con.cursor()
    
    
    def nullcheck(self, item):
        if item: return item
        else: return 'NULL'
    
    
    def crawl(self, page=None):
        '''describe
        '''
        pg = page if page else self.root
        # my container to hold property info
        d = PyQuery(url=pg)
        
        post_date  = d('h4').text()
        time_stamp = now
        
        apt_links = []
        for i, x in enumerate(d('p')):
            post_title = d('p').eq(i).text()
            post_url   = d('p').eq(i)('a').attr('href')
            location   = d('p').eq(i)('font').text()
            post_local = location.replace('(', '').replace(')', '')
            apt_links.append([post_title, post_url, post_local])
        
        
        for i, x in enumerate(apt_links):
            
        
        # parse title for price & bedrooms
        
        # post_date = '<body> Date:'
        #post_description = '<div id="userbody">'
        #post_id = '<div id="userbody"><font>'
        #time.sleep(0.2)
        #next_pg = ''
        #self.crawl(next_pg)
        

if __name__ == '__main__':
    spider = craigsSpider('craigslist.db3', 'http://austin.craigslist.org/apa/')
    # http://austin.craigslist.org/off/
    rs = spider.crawl()
    pprint(rs)
    
    
    
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
'''
apartments/housing
    title
    url
    price
    bedrooms
    location_phone
    date_posted
    description
    posting_id


-------
search for
----------

sqft
apartment name



$<price> / <n>br - <description> - (<location>--<phone>) <img>



'''