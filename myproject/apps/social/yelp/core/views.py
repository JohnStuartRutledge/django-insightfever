from django.template import Context, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.http import Http404
from django.shortcuts import render_to_response
from django.contrib.comments.views.comments import post_comment

from core.models import Event
import time
from datetime import date, datetime, timedelta
import calendar
import settings
import os


def preview_event(request, event_id):
    try:
        event = Event.objects.get(pk = event_id)
    except Event.DoesNotExist:
        raise Http404
    
    # fill in all fields of an event
    context = RequestContext(request, {'event' : event})
    return render_to_response("core/preview_event.html", context)


def preview_event_list(request):
    # get event ids
    maxEventNum = 100
    objs  = Event.objects.all()
    eList = []
    
    for obj in objs:
        maxEventNum -= 1
        if maxEventNum <= 0: break
        eList.append(obj.eventID)
    
    # get template
    tmpl = get_template('core/preview_event_list.html')
    
    # fill in event list context
    context = Context({'event_list' : eList})
    html    = tmpl.render(context)
    
    return HttpResponse(html)



########################### preview calendar ###

mnames = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def preview_calendar(request, year, month, change=None):
    """Listing of days in `month`."""
    year, month = int(year), int(month)
    print year, month, change

    # apply next / previous change
    if change in ('next', 'prev'):
        now, mdelta = date(year, month, 15), timedelta(days=31)
    if change == 'next':   mod = mdelta
    elif change == 'prev': mod = -mdelta
    year, month = (now+mod).timetuple()[:2]
    
    # init variables
    cal        = calendar.Calendar()
    month_days = cal.itermonthdays(year, month)
    nyear, nmonth, nday = time.localtime()[:3]
    lst  = [[]]
    week = 0
    
    # make month lists containing list of days for each week
    # each day tuple will contain list of entries and 'current' indicator
    for day in month_days:
        entries = current = False   # are there entries for this day; current day?
        if day:
            #entries = Entry.objects.filter(date__year=year, 
            # date__month=month, date__day=day)
            entries = Event.objects.filter(datePosted__year=year, 
                        datePosted__month=month, datePosted__day=day)
            if day == nday and year == nyear and month == nmonth:
                current = True
    
    lst[week].append((day, entries, current))
    if len(lst[week]) == 7:
        lst.append([])
        week += 1
    
    return render_to_response("core/preview_profile.html",
                dict(year=year,
                month=month,
                user=None,
                month_days=lst,
                mname=mnames[month-1],
                static_url=os.path.join(settings.SITE_URL,
                settings.STATIC_URL)))


def preview_calendar_day(request, year, month, day):
    """Listing of events in 'day'.
    """
    year, month, day = int(year), int(month), int(day)
    entries = Event.objects.filter(datePosted__year=year,
                                   datePosted__month=month, 
                                   datePosted__day=day)
    
    print len(entries)
    content = [];
    for entry in entries:
        content.append(render_event_unit(entry));
    
    return render_to_response("core/preview_calendar_day.html", 
                dict(year=year,
                month=month,
                day=day,
                user=None,
                mname=mnames[month-1],
                content=content))


def render_event_unit(event):
    tmpl = get_template("ui/event_unit.html")
    return tmpl.render(Context({'event' : event}));

