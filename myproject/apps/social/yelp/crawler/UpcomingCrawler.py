import os, sys
sys.path.append('../')
sys.path.append('../../')
import urllib
import json
import time
import datetime
from django.core.management import setup_environ
from evently import settings
from core.models import Event, Meetup
from crawler_utils import *

setup_environ(settings)


def encode(event):
    encodedFields = set(['description'])
    for k, v in event.iteritems():
        if k in encodedFields:
            # escape the encoding error
            s = v.encode(errors='ignore')
            event[k] = unicode(s)
    return event


def save_event_to_db(event):
    '''The function to save single event into DB (table: core_event)
    '''
    e = Event(
        categoryID             = parse_category_id(event['category_id']),
        datePosted             = parse_datetime(event['date_posted']),
        description            = event['description'],
        distance               = event['distance'],
        distanceUnits          = event['distance_units'],
        endDate                = parse_date(event['end_date']),
        endTime                = parse_time(event['end_time']),
        geoCodingAmbig         = event['geocoding_ambiguous'],
        geoCodingPrec          = event['geocoding_precision'],
        eventID                = event['id'],
        latitude               = event['latitude'],
        longitude              = event['longitude'],
        metroID                = event['metro_id'],
        name                   = event['name'],
        numFutureEvents        = event['num_future_events'],
        personal               = event['personal'],
        photoURL               = event['photo_url'],
        selfPromotion          = event['selfpromotion'],
        startDate              = parse_date(event['start_date']),
        startDateLastRendition = event['start_date_last_rendition'],
        startTime              = parse_time(event['start_time']),
        ticketFree             = parse_int(event['ticket_free']),
        ticketPrice            = event['ticket_price'],
        ticketURL              = event['ticket_url'],
        URL                    = event['url'],
        userID                 = event['user_id'],
        utcEnd                 = parse_datetime(event['utc_end']),
        utcStart               = parse_datetime(event['utc_start']),
        venueAddr              = event['venue_address'],
        venueCity              = event['venue_city'],
        venueCountryCode       = event['venue_country_code'],
        venueCountryID         = event['venue_country_id'],
        venueCountryName       = event['venue_country_name'],
        venueID                = event['venue_id'],
        venueName              = event['venue_name'],
        venueStateCode         = event['venue_state_code'],
        venueStateID           = event['venue_state_id'],
        venueStateName         = event['venue_state_name'],
        venueZip               = str(event['venue_zip']),
        watchListCount         = event['watchlist_count'])
    e.save()


class UpcomingCrawler:
    '''The class to collect data (events) from Web
    '''
    # Attributes
    api_key    = ''
    api_method = ''
    api_query  = 'http://upcoming.yahooapis.com/services/rest/'

    def __init__(self):
        self.api_key    = ''
        self.api_method = ''
        return

    def set_api_key(self, api_key):
        self.api_key = api_key
        return

    def set_api_method(self, api_method):
        self.api_method = api_method
        return

    def event_search(self, location):
        '''search 100 public events near the specific location
        Returns:
        event_list: a list of events, each of which is represented by \
        a dict object. All events are sorted based on distance
        '''
        get_query = '%s?api_key=%s&method=%s&location=%s&format=json' \
            % (self.api_query, self.api_key, self.api_method,
               urllib.quote(location, '/,'))

        res_stream = urllib.urlopen(get_query)
        res_data   = json.load(res_stream)
        event_list = res_data['rsp']['event']
        print "Successfully crawling %d events" % (len(event_list))
        return event_list

    def daily_event_search(self, location):
        search_count = 0
        while True:
            print search_count
            self.event_search(location)
            search_count = search_count + 1
            if search_count >= 5:
                break
            time.sleep(10)

if __name__ == '__main__':
    dc = UpcomingCrawler()
    dc.set_api_key('6b6117dc75')
    dc.set_api_method('event.search')
    events = dc.event_search('san francisco, ca')
    for event in events:
        event = encode(event)
        save_event_to_db(event)
        #break

    #dc.daily_event_search('san francisco, ca')
