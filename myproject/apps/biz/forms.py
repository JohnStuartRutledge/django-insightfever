from django import forms
from myproject.apps.biz.models import Business, Website, WebsiteTypes


class BusinessForm(forms.ModelForm):
    ''' Form that holds all info on for a particular business 
    '''
    class Meta:
        model   = Business
        exclude = ('members', 'slug', 'tags')


class WebsiteForm(forms.ModelForm):
    ''' Form that holds business website info
    '''
    site_type = forms.ModelChoiceField(
                        queryset=WebsiteTypes.objects.all(), empty_label=None)
    class Meta:
        model   = Website
        exclude = ('tags',)

