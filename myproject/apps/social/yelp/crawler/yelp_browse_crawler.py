import urllib
from datetime import datetime
from yelp_parsers import *
from django.core.management import setup_environ
from evently import settings
setup_environ(settings)
from core.models import YelpEventURL


print '========= Yelp Event Crawler ========='
print '1st Step: Obtain event links store in EventURL db.\n'

website = 'http://www.yelp.com'

# Start at the cities directory page, obtain all event cities
dir_url = 'http://www.yelp.com/locations?return_url=%2Fevents'
print 'Visiting: ' + dir_url
f = urllib.urlopen(dir_url)
s = f.read()

# Try and process the page.
yelp_dir_parser = YelpDirectoryParser()
yelp_dir_parser.parse(s)

# Get the eventlinks.
city_links = yelp_dir_parser.get_city_links()

# Then iterate through all the event cities, obtain 
# all the event URLs to store in EventURL database.
for city_link in city_links:
    browse_dir = city_link + '/browse'
    while browse_dir != None:
        print 'Visiting: ' + website + browse_dir
        try:
            f = urllib.urlopen(website + browse_dir)
        except URLError as e:
            if hasattr(e, 'reason'):
                print 'Failed to reach the server.'
                print 'Reason: ', e.reason
            elif hasattr(e, 'code'):
                print 'The server could\'t fulfill the request.'
                print 'Error code: ', e.code
            else:
                print 'Downloaded the page successfully.'
                s = f.read()
                # Try and process the page.
                yelp_browse_parser = YelpBrowseParser()
                yelp_browse_parser.parse(s)
                # Get the eventlinks.
                for event_link in yelp_browse_parser.get_eventlinks():
                    event_url = YelpEventURL()
                    event_url.eventURL = website + event_link
                    event_url.crawledTime = datetime.now() 
                    event_url.save()
            
            # Get thw browse page's next link
            browse_dir = yelp_browse_parser.get_next_browse_link()
