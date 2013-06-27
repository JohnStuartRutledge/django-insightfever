'''
Example geocoder for Django
'''
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import simplejson as json
from django.utils.http import urlquote

import requests


class Geocoder(object):
    def __init__(self):
        self.mapquest_api_url = getattr(settings, "MAPQUEST_API_URL", None)
        if not self.mapquest_api_url:
            raise ImproperlyConfigured("MAPQUEST_API_URL does not exist in "
                "the settings file.")

    def mapquest_geocode(self, location=None):
        """ MapQuest specific geocoder API call.
        """
        if not location:
            return {"error": "No location was received.", "status": False}

        result = requests.get(
            self.mapquest_api_url + "&location=%s" % (urlquote(location)))

        if result.status_code == 200:
            data = json.loads(result.content)
            try:
                lat = data["results"][0]["locations"][0]["displayLatLng"]["lat"]
                lng = data["results"][0]["locations"][0]["displayLatLng"]["lng"]
                return {
                    "point" : u"POINT(%s %s)" % (lng, lat),
                    "status": True
                    }
            except KeyError:
                return {
                    "error" : "MapQuest found no data for the location entered.",
                    "status": False
                    }
        return {
            "error" : "Problem communicating with MapQuest. Please try again.",
            "status": False
            }


#-----------------------------------------------------------------------------
# EXAMPLE OF HOW TO USE Geocoder in VIEWS
#-----------------------------------------------------------------------------
from django.contrib.gis.geos import *

class GeoView(FormView):
    from_class = searchForm
    template_name = "geo.html"

    def form_valid(self, form):
        location = form.cleaned_data["location"]
        distance = form.cleaned_data["distance"]
        units    = form.cleaned_data["units"]

        point = Geocoder().mapquest_geocode(location)

        if point["status"]:
            queryset = self.model.objects.select_related("user").exclude(
                point__isnull=True).distance(point["point"])

            if units == "km":
                queryset = queryset.filter(point__distance_lte=(
                    point["point"], D(km=distance)))
            else:
                queryset = queryset.filter(point__distance_lte=(
                    point["point"], D(mi=distance)))

            queryset = queryset.order_by("distance")

        return self.render_to_response({
            "object_list": queryset, 
            "form"       : form,
            "units"      : units
            })



#-----------------------------------------------------------------------------
# FORMS.def
#-----------------------------------------------------------------------------
import floppyforms as forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Field, HTML
from crispy_forms.bootstrap import FormActions


class SearchForm(forms.Form):
    location = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "span11",
                "placeholder": "Enter a location"
            }
        ),
    )
    distance = forms.IntegerField(
        initial=50,
        label='',
        widget=forms.NumberInput(attrs={
            "class": "input-small",
            "min": 1,
            "max": 6000,
        })
    )
    units = forms.ChoiceField(
        choices=(
            ("km", "km"),
            ("mi", "mi")
        ),
        label='',
        widget=forms.Select(attrs={
            "class": "input-small"
        })
    )

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = "well form-inline"
        self.helper.form_method = "POST"
        self.helper.layout = Layout(
            "location",
            Div(
                HTML('<label for="id_distance" class="control-label '
                     'requiredField">Distance*</label><br>'),
                Div(
                    Field("distance", template="bootstrap/custom-field.html"),
                    Field("units", template="bootstrap/custom-field.html"),
                    css_class="controls"
                ),
                css_class="clearfix control-group"
            ),
            FormActions(
                Submit("search", "Search", css_class="btn btn-info"),
            )
        )
        super(SearchForm, self).__init__(*args, **kwargs)


