# -*- coding: utf-8 -*-

'''
INSIGHT FEVER WEB CRAWLER
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
from cgi import escape
from pprint import pprint
from datetime import datetime
from traceback import format_exc
from pyquery import PyQuery as pq
from Queue import Queue, Empty as QueueEmpty

# USE THESE TWO LIBRARIES
# import requests
# import furl

#>>> r = requests.get('https://api.github.com', auth=('user', 'pass'))

# make a git request
url = 'http://www.insightfever.com'
r = requests.get(url)
r.text        # the raw html
r.status_code # 200, 404, etc
r.headers     # dictionary of headers

# to raise an error in response to a bad request
r.raise_for_status() # if r.status_code == 200 this would do nothing

# use r.history() to get a list of request objects created for the given request
r.history

# a typical response would be: [<Response [301]>]
# aka we were redirected.

# to disable redirects
r = request.get(url, allow_redirects=False)

# set a timeout so that you can move on if you don't get a response
request.get(url, timeout=0.001)


r.config['base_headers']['User-Agent'] = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.14) Gecko/20080418 Ubuntu/7.10 (gutsy) Firefox/2.0.0.14'


# example of using requests on twitter API
import requests
import json

r = requests.post('https://stream.twitter.com/1/statuses/filter.json',
        data={'track': 'requests'}, auth=('username', 'password'))

for line in r.iter_lines():
    # filter out keep-alive new lines
    if line: print json.loads(line)

#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------

now = datetime.now()

AGENT = 'User-Agent','Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.14) Gecko/20080418 Ubuntu/7.10 (gutsy) Firefox/2.0.0.14'

#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------

class FeverSpider:
    
    def __init__(self, db_name, root, depth, max_links, locked=True):
        '''
        INSIGHT FEVER WEB-CRAWLER
        @db_name    - name of the database to store scrappings
        @root       - root url from which to begin the scrape
        @depth      - recursion max depth
        @max_links  - max number of links obtained per url
        @locked     - if True crawler avoids sites outside of root
        '''
        self.locked    = locked
        self.root      = root
        self.host      = urlparse.urlparse(root)[1]
        self.depth     = depth    
        self.max_links = max_links
        self.urls      = []
        self.links     = 0
        self.hit_count = 0
        
        # connect to sqlite DB
        db  = os.path.join(os.getcwd(), db_name)
        con = sqlite3.connect(db)
        cur = con.cursor()
        
    
    def getPage(self, page_url):
        '''get a webpage'''
        d = pq(url=page_url)
    
    
    def crawl(self, start_url=self.root):
        '''describe'''
        page = Fetcher(start_url)
        page.fetch()
        q = Queue()
        
        # put the pages urls into the queue
        for url in page.urls: q.put(url)
        followed = [start_url]
        
        n = 0
        while True:
            # pull a URL out of the queue
            try: url = q.get()
            except QueueEmpty: break
            n += 1
            
            # if you have not yet visited this URL
            if url not in followed:
                try:
                    host = urlparse.urlparse(url)[1]
                    # make sure we only follow links w/in the site
                    if self.locked and re.match('.*%s' % self.host, host):
                        followed.append(url)
                        self.hit_count += 1
                        
                        # fetch HTML using first URL in queue
                        page = Fetcher(url)
                        page.fetch()
                        for i, url in enumerate(page):
                            if url not in self.urls:
                                self.links += 1
                                q.put(url)
                                self.urls.append(url)
                        
                        # if the recusion depth has been exceeded
                        if n > self.depth and self.depth > 0:
                            break
                
                except Exception, err:
                    print 'ERROR: Cannot process url "%s" (%s)' % (url, err)
                    print format_exc()


class Fetcher(object):
    
    def __init__(self, url):
        '''fetch a page for a given url, as 
        well as all the links embeded w/in it.
        '''
        self.url  = url
        self.urls = []
    
    def __getitem__(self, x):
        '''return a specific url from urls dict'''
        return self.urls[x]
    
    def _addHeaders(self, request):
        '''Add user-agent and other URL headers'''
        request.add_header('User-Agent', AGENT)
        # TODO - add more headers
    
    def getcookies(self, cookiejar, host, path):
        pass
    
    def setcookies(self, cookiejar, host, lines):
        pass
    
    def open(self):
        '''Open a URL with urllib2
        '''
        try:
            request = urllib2.Request(self.url)
            handle  = urllib2.build_opener()
        except IOError: return None
        return (request, handle)
    
    def fetch(self):
        '''DESCRIBE
        '''
        request, handle = self.open()
        self._addHeaders(request)
        if handle:
            try:
                content = unicode(handle.open(request).read(), 
                                  "utf-8", errors="replace")
            except urllib2.HTTPError, error:
                if error.code == 404:
                    print >> sys.stderr, "ERROR: %s -> %s" % (error, error.url)
                else:
                    print >> sys.stderr, "ERROR: %s" % error
                tags = []
            
            except urllib2.URLError, error:
                print >> sys.stderr, "ERROR: %s" % error
                tags = []
            
            # add new urls to the urls list
            for tag in tags:
                href = tag.get("href")
                if href is not None:
                    url = urlparse.urljoin(self.url, escape(href))
                    if url not in self:
                        self.urls.append(url)
    



if __name__ == '__main__':
    db_name   = 'yellowpages.db3'
    root      = 'http://www.yellowpages.com/austin-tx/'
    depth     = 2
    max_links = 99
    locked    = True
    start_url = "http://www.yellowpages.com/austin-tx/apartments?g=Austin%2C+TX&order=name&refinements%5Bheadingtext%5D=Apartments"
    
    spider = FeverSpider('yellowpages.db3', root, depth, max_links, locked)
    spider.crawl(start_url)

