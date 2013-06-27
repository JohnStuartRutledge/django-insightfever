import urllib
from yelp_parsers import *
from django.core.management import setup_environ
from evently import settings
setup_environ(settings)
from core.models import YelpEvent, YelpEventURL


print '''Usage: 
    - You need to run yelp_browse_crawler.py to store all the event 
      URLs to the YelpEventURL db first.
    - This event crawlser only visits the event pages in the YelpEventURL
      db to obtain useful event details.
    - Event details are stored to YelpEvent db.
    - By design, if a event URL is already explored before, (has details
      stored in YelpEvent db), this URL will not be explored.'''


event_urls = YelpEventURL.objects.all()
for event_url_obj in event_urls:
    event_url = event_url_obj.eventURL;
    # Test to see if the the page is already visited:
    if len(YelpEvent.objects.filter(eventURL=event_url)) > 0:
        print 'Yelp Event is visited, ignore : ' + event_url
    else:
        print 'Visiting: ' + event_url
        try:
            f = urllib.urlopen(event_url)
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
                # The class should have been defined first, remember.
                yelp_event = YelpEvent()
                yelp_event.eventURL   = event_url
                yelp_eventpage_parser = YelpEventPageParser()
                yelp_eventpage_parser.parse(s, yelp_event)
                # Save Event to db:
                yelp_event.save()
