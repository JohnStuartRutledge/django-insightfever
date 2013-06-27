from django.utils.translation import ugettext_lazy as _
from django import forms
from django.db import models
from django.forms import fields
from django.forms.util import to_current_timezone
from django.template.loader import render_to_string
from django.forms.widgets import Select, MultiWidget, DateInput, TextInput

from django.utils.text import capfirst
from django.core import exceptions
from django.db.models import get_model

# needed for South compatibility
#from south.modelsinspector import add_introspection_rules
#add_introspection_rules([], ["^coop\.utils\.fields\.MultiSelectField"])
from datetime import datetime
from time import strptime, strftime
from dateutil.relativedelta import relativedelta
import dateutil.parser

from myproject.apps.social.models import PostQueue
from myproject.apps.biz.models import Business


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
    # widget mostly taken from:
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
                   TextInput(attrs=time_attrs),
                   TextInput(attrs=time_attrs),
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
        return u"""\
        <div class="control-group">
            <table id="post_queue_datetime_table">
                <tbody>
                <tr>
                    <td class="post_queue_date_field">{0}</td>
                    <td>
                        <span class="post_queue_time">{1}</span>:
                        <span class="post_queue_time">{2}</span>
                        <span id="ampm">{3}</span>
                    </td>
                </tr>
                <tr>
                    <td class="post_queue_date_field"></td>
                    <td id="time_helper" class="help-block"></td>
                </tr>
                </tbody>
            </table>
        </div>
        """.format(
            rendered_widgets[0], rendered_widgets[1],
            rendered_widgets[2], rendered_widgets[3])


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
        """ We have to pass a list of field types to the constructor,
        otherwise we will not get any data to our compress method.
        """
        all_fields = (
            fields.CharField(max_length=10),
            fields.CharField(max_length=2),
            fields.CharField(max_length=2),
            fields.ChoiceField(choices=[('AM','AM'),('PM','PM')])
            )
        super(SplitDateTimeField, self).__init__(all_fields, *args, **kwargs)

    def compress(self, data_list):
        """ Takes the values from the MultiWidget and passes them
        as a list to this function. This function needs to compress
        the list into a single object to save.
        """
        if data_list:
            if not (data_list[0] and data_list[1] and data_list[2] and data_list[3]):
                raise forms.ValidationError("Field is missing data.")

            input_time = strptime(u"{0}:{1} {2}".format(
                         data_list[1], data_list[2], data_list[3]), "%I:%M %p")
            datetime_string = u"{0} {1}".format(data_list[0],
                                              strftime('%H:%M', input_time))
            return datetime_string
        return None


class MultiSelectFormField(forms.MultipleChoiceField):
    '''
    http://djangosnippets.org/snippets/2753/
    This field implements a model field and an accompanying formfield to store
    multiple choices as a comma-separated list of values, using the normal
    CHOICES attribute.

    You'll need to set maxlength long enough to cope with the maximum number
    of choices, plus a comma for each.

    The normal get_FOO_display() method returns a comma-delimited string of
    the expanded values of the selected choices.

    The formfield takes an optional max_choices parameter to validate a maximum
    number of choices.
    '''
    widget = forms.CheckboxSelectMultiple

    def __init__(self, *args, **kwargs):
        self.max_choices = kwargs.pop('max_choices', 0)
        super(MultiSelectFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if not value and self.required:
            raise forms.ValidationError(self.error_messages['required'])
        # if value and self.max_choices and len(value) > self.max_choices:
        #     raise forms.ValidationError('You must select a maximum of %s choice%s.'
        #             % (apnumber(self.max_choices), pluralize(self.max_choices)))
        return value


class MultiSelectField(models.Field):
    '''
    http://djangosnippets.org/snippets/2753/

    NOTE: to get this to work with south you must:
    from south.modelsinspector import add_instrospection_rules
    add_instrospection_rules([], ["^appname\.fields\.MultiSelectField"])
    '''
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return "CharField"

    def get_choices_default(self):
        return self.get_choices(include_blank=False)

    def _get_FIELD_display(self, field):
        value = getattr(self, field.attname)
        choicedict = dict(field.choices)

    def formfield(self, **kwargs):
        # don't call super, as that overrides default widget if it has choices
        defaults = {
            'required':  not self.blank,
            'label':     capfirst(self.verbose_name),
            'help_text': self.help_text,
            'choices':   self.choices
            }
        if self.has_default():
            defaults['initial'] = self.get_default()
        defaults.update(kwargs)
        return MultiSelectFormField(**defaults)

    def get_prep_value(self, value):
        return value

    def get_db_prep_value(self, value, connection=None, prepared=False):
        if isinstance(value, basestring):
            return value
        elif isinstance(value, list):
            return ",".join(value)

    def to_python(self, value):
        if value is not None:
            return value if isinstance(value, list) else value.split(',')
        return ''

    def contribute_to_class(self, cls, name):
        #raise Exception(cls, name)
        super(MultiSelectField, self).contribute_to_class(cls, name)
        if self.choices:
            choices = dict(self.choices)
            def func(self, fieldname=name, choicedict=choices):
                return ','.join([choicedict.get(x, x) for x in getattr(self, fieldname)])

            setattr(cls, 'get_%s_display' % self.name, func)

    def validate(self, value, model_instance):
        arr_choices = self.get_choices_selected(self.get_choices_default())
        for opt_select in value:
            if (int(opt_select) not in arr_choices):  # the int() here is for comparing with integer choices
                raise exceptions.ValidationError(self.error_messages['invalid_choice'] % value)
        return

    def get_choices_selected(self, arr_choices=''):
        if not arr_choices:
            return False
        list = []
        for choice_selected in arr_choices:
            list.append(choice_selected[0])
        return list

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)


#-----------------------------------------------------------------------------
# FORMS
#-----------------------------------------------------------------------------

class UploadForm(forms.Form):
    file_cat = forms.ChoiceField(choices=FILE_CATEGORIES)
    file = forms.FileField(label='Select a file', help_text='max. 42 megabytes')



class PostQueueForm(forms.ModelForm):
    '''Form for scheduling posts to Facebook and Twitter
    '''
    social_sites = forms.MultipleChoiceField(choices=SOCIAL_SITE_CHOICES,
                        widget=forms.CheckboxSelectMultiple())

    post_date    = SplitDateTimeField(widget=PostQueueDateWidget(
                        attrs={'date_class':'datepicker span2',
                               'time_class':'timepicker span1'}))
    status       = forms.ChoiceField(choices=STATUS_CHOICES,
                        widget=forms.RadioSelect)

    class Meta:
        model   = PostQueue
        fields  = ('message','social_sites', 'post_date', 'biz')
        widgets = {
            'message': forms.Textarea(attrs={'cols':30,'rows':10,'class':'input-xlarge'}),
        }

    def clean_post_date(self):
        ''' Make sure that the submitted post date is scheduled to post
        for a time that has already passed. Also limit posts to only 6 months
        in the future as per Facebooks scheduled post policy.
        '''
        data = self.cleaned_data['post_date']
        publish_time = dateutil.parser.parse(data)
        now = datetime.now()

        # if scheduled_publish_time is in the past return an error
        if publish_time < now:
            raise forms.ValidationError('You cannot schedule a post for a time in the past.')

        # if publish time is greater than six months from now, return error
        if publish_time > now+relativedelta(months=+6):
            raise forms.ValidationError('You cannot schedule a post beyond six months from today.')
        return data




class PostQueueUpdateForm(forms.Form):
    '''Form for scheduling posts to Facebook and Twitter
    '''
    #def __init__(self, *args, **kwargs):
    #    super(PostQueueUpdateForm, self).__init__(*args, **kwargs)

    #biz          = forms.ModelChoiceField(queryset=Business.objects.all())
    social_sites = MultiSelectFormField(choices=SOCIAL_SITE_CHOICES)
    post_date    = SplitDateTimeField(widget=PostQueueDateWidget(
                        attrs={'date_class':'datepicker span2',
                               'time_class':'timepicker span1'}))
    status        = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.RadioSelect)

    class Meta:
        #model   = get_model('myproject.apps.social.models', 'PostQueue')
        fields  = ('message','social_sites', 'post_date', 'biz')
        widgets = {
            'message': forms.Textarea(attrs={'cols':30,'rows':10,'class':'input-xlarge'}),
        }

