# -*- coding: utf-8 -*-

'''
INSIGHT FEVER WEB CRAWLER
'''
import os
import re
import sys
import sqlite3
import requests
from furl import furl
from datetime import datetime
from pyquery import PyQuery
from Queue import Queue, Empty as QueueEmpty

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

class UserAgentError(Exception):
    pass

#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------

class FeverSpider(object):
    
    def __init__(self, db_name, start_URL, agent_type, depth, max_links, locked=True):
        '''
        INSIGHT FEVER WEB-CRAWLER
        @db_name    - name of the database to store scrappings
        @root       - root url from which to begin the scrape
        @depth      - recursion max depth
        @max_links  - max number of links obtained per url
        @locked     - if True crawler avoids sites outside of root
        '''
        self.locked    = locked
        self.start_URL = start_URL
        self.AGENT     = self._set_agent(agent_type)
        self.host      = furl(start_URL).host
        self.depth     = depth
        self.max_links = max_links
        self.links     = 0
        self.hit_count = 0
        
        # connect to sqlite DB
        db  = os.path.join(os.getcwd(), db_name)
        con = sqlite3.connect(db)
        cur = con.cursor()
        
        # put the starting site into the URLS queue
        #self.urls.put(self.start_URL)
    
    @staticmethod
    def _set_agent(agent_type="Mozilla"):
        '''Set your user agent
        '''
        if agent_type == 'Mozilla':
            AGENT = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.14) \
            Gecko/20080418 Ubuntu/7.10 (gutsy) Firefox/2.0.0.14'
        elif agent_type == 'Fever':
            AGENT = 'InsightFever Bot'
        else:
            raise UserAgentError
        
        return AGENT
        # TODO - add more to this function
    
    def crawl(self, page=None):
        '''Crawl a webpage looking for content
        '''
        pg = page if page else HtmlPage(self.start_URL)
        q  = Queue()
        
        # set your UserAgent
        pg.r.config['base_headers']['User-Agent'] = self.AGENT
        
        # put the pages urls into the queue
        for url in pg.getUrls():
            q.put(url)
        
        # cross off the start_URL from the list
        followed = [self.start_URL]
        
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
                        pg = HtmlPage(url)
                        pg.fetch()
                        for i, url in enumerate(pg):
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


class HtmlPage(object):
    
    def __init__(self, url):
        '''Create an object that stores all relevant information
        about a specific URL, including the raw HTML, the pquery
        tagged HTML, and other convenience methods.
        '''
        self.url  = url
        self.urls = []
        self.r    = requests.get(self.url)
        self.html = PyQuery(self.r.text)
        
    
    def __getitem__(self, x):
        '''return a specific url from urls dict
        '''
        return self.urls[x]
    
    
    def getUrls(self):
        '''return all urls on a given page
        '''
        urls = [furl(url) for url in set(a.attrib['href'] for a in self.html.find('a'))]
        
        for x in urls:
            # find relative paths and generate a full url from them
            if x.url.startswith('/'):
                pass
        
        
        # remove all external sites if the locked setting is true
        if self.locked:
            for url in urls:
                # assuming a url host exists for this variable
                if url.host: 
                    # check to see if its an external link, if it is, delete it
                    if not url.host == self.host:
                        del(urls[url])
             
        return urls
        
    
    def fetch(self):
        '''DESCRIBE
        '''
        if r.status_code == 200:
            tags = []
            # add new urls to the urls list
            for tag in tags:
                href = tag.get("href")
                if href is not None:
                    url = urlparse.urljoin(self.url, escape(href))
                    if url not in self:
                        self.urls.append(url)
    



if __name__ == '__main__':
    db_name   = 'test.db3'
    start_URL = 'http://www.insightfever.com'
    depth     = 2
    max_links = 99
    locked    = True
    
    spider = FeverSpider(db_name, start_URL, depth, max_links, locked)
    
    spider.crawl(start_url)

