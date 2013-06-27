from django.utils.translation import ugettext_lazy as _
from django import forms
from django.db import models
from django.forms import fields
from django.forms.util import to_current_timezone
from django.template.loader import render_to_string
from django.forms.widgets import Select, MultiWidget, DateInput, TextInput

from datetime import datetime
from time import strptime, strftime
from myproject.apps.social.models import PostQueue


FILE_CATEGORIES = (
        ('yelp',       _('yelp')),
        ('aptratings', _('aptratings')),
        ('fbook',      _('fbook insights'))
    )

SOCIAL_SITE_CHOICES = (
        ('twitter',  _('Twitter')),
        ('facebook', _('Facebook')),
    )

STATUS_CHOICES = (
        ('active',   _('active')),
        ('inactive', _('inactive')),
        ('delete',   _('delete')),
    )

#-----------------------------------------------------------------------------
# WIDGETS 
#-----------------------------------------------------------------------------

class PostQueueDateWidget(MultiWidget):
    # widget modified from code taken from:
    # http://copiesofcopies.org/webl/2010/04/26/a-better-datetime-widget-for-django/
    def __init__(self, attrs=None, date_format=None, time_format=None):
        date_class = attrs['date_class']
        time_class = attrs['time_class']
        del attrs['date_class']
        del attrs['time_class']
        time_attrs = attrs.copy()
        time_attrs['class'] = time_class
        date_attrs = attrs.copy()
        date_attrs['class'] = date_class
        date_attrs['value'] = datetime.now().strftime("%Y-%m-%d")
        
        widgets = (DateInput(attrs=date_attrs, format=date_format), 
                   TextInput(attrs=time_attrs), TextInput(attrs=time_attrs), 
                   Select(attrs=time_attrs, choices=[('AM','AM'),('PM','PM')]))
        
        super(PostQueueDateWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            d        = strftime("%Y-%m-%d", value.timetuple())
            hour     = strftime("%I", value.timetuple())
            minute   = strftime("%M", value.timetuple())
            meridian = strftime("%p", value.timetuple())
            return (d, hour, minute, meridian)
        else:
            return (None, None, None, None)


    def format_output(self, rendered_widgets):
        '''Returns unicode HTML string of the rendered form/widgets
        '''
        return u"""Date: {0}<br/>Time: {1}:{2} {3}""".format(
            rendered_widgets[0], rendered_widgets[1],
            rendered_widgets[2], rendered_widgets[3])

    #class Media:
    #    css = {}
    #    js = ("js/datepicker.js", )


#-----------------------------------------------------------------------------
# FIELDS 
#-----------------------------------------------------------------------------

class SplitDateTimeField(fields.MultiValueField):
    widget = PostQueueDateWidget
    default_error_messages = {
        'invalid_date': _(u'Enter a valid date.'),
        'invalid_time': _(u'Enter a valid time.'),
    }

    def __init__(self, *args, **kwargs):
        ''' Pass a list of field types to the constructor, 
        or else we won't get any data to our compress method.
        '''
        all_fields = (
            fields.CharField(max_length=10),
            fields.CharField(max_length=2),
            fields.CharField(max_length=2),
            fields.ChoiceField(choices=[('AM','AM'),('PM','PM')])
            )
        super(SplitDateTimeField, self).__init__(all_fields, *args, **kwargs)
    
    def compress(self, data_list):
        ''' Take values from the MultiWidget and pass them as a list to this 
        function which needs to compress the list into a single object to save.
        '''
        if data_list:
            if not (data_list[0] and data_list[1] and data_list[2] and data_list[3]):
                raise forms.ValidationError("Field is missing data.")

            input_time = strptime(u"{0}:{1} {2}".format(
                         data_list[1], data_list[2], data_list[3]), "%I:%M %p")
            datetime_string = u"{0} {1}".format(data_list[0],
                                              strftime('%H:%M', input_time))
            return datetime_string
        return None


#-----------------------------------------------------------------------------
# FORMS
#-----------------------------------------------------------------------------

class PostQueueForm(forms.ModelForm):
    ''' Form for scheduling posts to Facebook and Twitter
    '''
    social_sites = forms.MultipleChoiceField(choices=SOCIAL_SITE_CHOICES,
                        widget=forms.CheckboxSelectMultiple())
    post_date = SplitDateTimeField(widget=PostQueueDateWidget(
                        attrs={'date_class':'datepicker span2',
                               'time_class':'timepicker span1'}))
    status = forms.ChoiceField(choices=STATUS_CHOICES,
                        widget=forms.RadioSelect)

    class Meta:
        model = PostQueue
        fields  = ('message', 'social_sites', 'post_date', 'biz')
        widgets = {
            'message': forms.Textarea(
                attrs={'cols':30,'rows':10,'class':'input-xlarge'}),
            }



