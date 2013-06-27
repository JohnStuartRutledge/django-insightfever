import os, sys
import UpcomingCrawler

if __name__ == '__main__':
    dc = UpcomingCrawler.UpcomingCrawler()
    dc.set_api_key('6b6117dc75')
    dc.set_api_method('event.search')
    event_list = dc.event_search('san francisco, ca')
    #dc.daily_event_search('san francisco, ca')
    print len(event_list)
    key_list = sorted(event_list[0].keys())
    for key in key_list:
        print key, ':', event_list[0][key]
