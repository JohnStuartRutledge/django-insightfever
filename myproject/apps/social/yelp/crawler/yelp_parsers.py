import sys
sys.path.append('../')
sys.path.append('../../')
import sgmllib
import dateutil.parser
from datetime import datetime
from django.core.management import setup_environ
from evently import settings
setup_environ(settings)
from core.models import YelpEvent

class YelpDirectoryParser(sgmllib.SGMLParser):
    '''A parser to parse the ALL Event Loctions directory page of yelp.com
    '''
    def parse(self, s):
        self.feed(s)
        self.close()
        print "Page Parsed."

    def __init__(self, verbose = 0):
        "Initialize object, pass 'verbose' to supperclass."
        sgmllib.SGMLParser.__init__(self, verbose)
        self.city_links = []
        self.within_cities_block = False

    def start_ul(self, attributes):
        for name, value in attributes:
            if name == 'class' and value == 'cities':
                self.within_cities_block = True
                break

    def end_ul(self):
        self.within_cities_block = False

    def start_a(self, attributes):
        if self.within_cities_block == True:
            for name, value in attributes:
                if name == 'href':
                    self.city_links.append(value)

    def get_city_links(self):
        return self.city_links


class YelpBrowseParser(sgmllib.SGMLParser):
    "A parser to parse the browse page of yelp class."

    def parse(self, s):
        "Parse the given string 's'."
        self.feed(s)
        self.close()
        print "Page Parsed."

    def __init__(self, verbose=0):
        "Initialize an object, passing 'verbose' to the superclass."
        sgmllib.SGMLParser.__init__(self, verbose)
        self.eventlinks              = []
        self.next_browse_link        = None
        self.within_main_events_list = False
        self.is_event_href           = False

    def start_ul(self, attributes):
        "Mark the beginning and ending of main_events_list block.\
        Only Process events that within the main_events_list table."
        for name, value in attributes:
            if name == "id" and value == "main_events_list":
                self.within_main_events_list = True
                break

    def end_ul(self):
        self.within_main_events_list = False

    def start_a(self, attributes):
        "Mark the beginning and ending of url summary.\
        Remember the pager_page_next to continue the event list."
        if self.within_main_events_list == False:
            # Try to find the next page link
            for name, value in attributes:
                if name == "id" and value == "pager_page_next":
                    for name2, value2 in attributes:
                        if name2 == "href":
                            self.next_browse_link = value2
                            break
                    break
        else:
            # if within the main_events_list remember events
            for name, value in attributes:
                if name == "class" and value == "url summary":
                    self.is_event_href = True
                    for name2, value2 in attributes:
                        if name2 == "href":
                            self.eventlinks.append(value2)
                            break
                    break

    def end_a(self):
        self.is_event_href = False

    def get_eventlinks(self):
        "Return the list of eventlinks."
        return self.eventlinks

    def get_next_browse_link(self):
        "Return the next browse link."
        return self.next_browse_link


# A parser to parse a paticular event page of yelp.com
class YelpEventPageParser(sgmllib.SGMLParser):
    "A parser class configured to parse the event page of yelp.com"

    class ItemType:
        NONE         = 0
        PHOTO        = 1
        CATEGORY     = 2
        ADDRESS      = 3
        HOW          = 4
        COST         = 5
        DESCRIPTION  = 6
        NAME         = 7
        TIME         = 8
        LOCATIONNAME = 9
        ATTENDCOUNT  = 10

    def __init__(self, verbose=0):
        "Initialise an object, passing 'verbose' to the superclass."
        sgmllib.SGMLParser.__init__(self, verbose)
        self.item_type      = self.ItemType.NONE
        self.within_dt      = False
        self.yelp_event     = None
        self.addr_attribute = None


    def parse(self, s, yelp_event):
        "Parse the given string 's'."
        self.yelp_event = yelp_event
        self.feed(s)
        self.close()
        yelp_event.crawledTime = datetime.now()
        print "Page Parsed."

    def start_a(self, attributes):
        if self.item_type == self.ItemType.HOW:
            for name, value in attributes:
                if name == 'href':
                    self.yelp_event.how = value
        for name, value in attributes:
            if name == "id" and value == "main_event_photo":
                self.item_type = self.ItemType.PHOTO
                break

    def end_a(self):
        if self.item_type == self.ItemType.PHOTO:
            self.item_type = self.ItemType.NONE

    def start_img(self, attributes):
        if self.item_type == self.ItemType.PHOTO:
            for name, value in attributes:
                if name == 'src':
                    self.yelp_event.photoURL = value

    def start_h1(self, attributes):
        for name, value in attributes:
            if name == 'id' and value == 'event_name':
                self.item_type = self.ItemType.NAME

    def end_h1(self):
        self.item_type = self.ItemType.NONE

    def start_dt(self, attributes):
        self.within_dt = True

    def end_dt(self):
        self.within_dt = False

    def start_dd(self, attributes):
        pass

    def end_dd(self):
        self.item_type = self.ItemType.NONE

    def start_dl(self, attributes):
        pass

    def end_dl(self):
        self.item_type = self.ItemType.NONE


    def start_abbr(self, attributes):
        assert self.item_type == self.ItemType.TIME
        for name, value in attributes:
            if name == "title":
                t = dateutil.parser.parse(value)
                # NOTE: timezone is IGNORED, django does not support timezone aware time
                t = t.replace(tzinfo=None)
                for name2, value2 in attributes:
                    if name2 == "class" and value2 == "dtstart":
                        self.yelp_event.utcStart = t
                        break
                    elif name2 == "class" and value2 == "dtend":
                        self.yelp_event.utcEnd = t
                        break
                break

    def start_span(self, attributes):
        if self.item_type == self.ItemType.ADDRESS:
            for name, value in attributes:
                if name == "class":
                    self.addr_attribute = value
                    break
        for name, value in attributes:
            if name == 'id' and value == 'subscriber_count':
                self.item_type = self.ItemType.ATTENDCOUNT
                break

    def end_span(self):
        if self.item_type == self.ItemType.ATTENDCOUNT:
            self.item_type = self.ItemType.NONE
        self.addr_attribute = None

    def start_h2(self, attributes):
        for name, value in attributes:
            if name == 'id' and value == 'location_name':
                self.item_type = self.ItemType.LOCATIONNAME

    def end_h2(self):
        self.item_type = self.ItemType.NONE


    def handle_data(self, value):
        if self.within_dt == True:
            if value == "Category:": self.item_type = self.ItemType.CATEGORY
            if value == "When:":     self.item_type = self.ItemType.TIME
            if value == "Where:":    self.item_type = self.ItemType.ADDRESS
            if value == "How:":      self.item_type = self.ItemType.HOW
            if value == "Cost:":     self.item_type = self.ItemType.COST
            if value == "What/Why:": self.item_type = self.ItemType.DESCRIPTION
            return

        if self.item_type == self.ItemType.ADDRESS:
            if self.addr_attribute == "street-address": self.yelp_event.venueAddr = value
            elif self.addr_attribute == "locality":     self.yelp_event.venueCity = value
            elif self.addr_attribute == "region":       self.yelp_event.venueStateName = value
            elif self.addr_attribute == "postal-code":  self.yelp_event.venueZip = value

        elif self.item_type == self.ItemType.COST:
            if value != None:
                self.yelp_event.cost += value.strip()
        elif self.item_type == self.ItemType.DESCRIPTION:
            self.yelp_event.description += value
        elif self.item_type == self.ItemType.LOCATIONNAME:
            self.yelp_event.venueName = value
        elif self.item_type == self.ItemType.ATTENDCOUNT:
            strs = value.split()
            if len(strs) > 0:
                self.yelp_event.watchListCount = int(strs[0])

