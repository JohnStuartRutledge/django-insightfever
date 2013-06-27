from django.utils.translation import ugettext_lazy as _
from django import forms
#from django.forms.widgets import Select
from myproject.apps.social.facebook.models import FacebookManagedPages
#from myproject.fever_utils import get_user_businesses

#-----------------------------------------------------------------------------
# FORMS
#-----------------------------------------------------------------------------


class FbookPageForm(forms.ModelForm):
    ''' Form for grabbing and saving data about managed Facebook pages
    USE THIS VIEW WHEN ATTEMPTING THE MODELFORMSET APPROACH 
    ''' 
    def __init__(self, *args, **kwargs):
        super(FbookPageForm, self).__init__(*args, **kwargs)
        #for key in self.fields:
        #    self.fields[key].required = False

        self.fields['biz'].label = 'Business'
        self.fields['biz'].widget.attrs['class'] = 'biz_name'
        self.fields['name'].label = 'Page'
        self.fields['name'].widget = forms.TextInput()
        self.fields['name'].widget.attrs['class'] = 'input-xlarge'
        self.fields['name'].widget.attrs['readonly'] = True
        self.fields['name'].required = False

    def clean(self):
        cleaned_data = super(FbookPageForm, self).clean()
        return cleaned_data 

    class Meta:
        model   = FacebookManagedPages
        exclude = ('user', 'category', 'fbook_uid', 
                   'perms', 'access_token')
        fields  = ('name', 'biz', 'ignored')


#-----------------------------------------------------------------------------
# 
#-----------------------------------------------------------------------------
"""

class SaveFbookPageForm(forms.ModelForm):
    ''' Form for grabbing and saving data about managed Facebook pages 
    '''
    #facebook_pages   = forms.CharField(widget=forms.Select(choices=[]))
    #managed_business = forms.CharField(widget=forms.Select(choices=[]))

    def __init__(self, request, pages, *args, **kwargs):
        super(SaveFbookPageForm, self).__init__(*args, **kwargs)

        self.MANAGED_BIZ_CHOICES = tuple(
            [(u'', '')] + [(x.biz_name.lower(), _(x.biz_name)) 
            for x in get_user_businesses(request.user)])

        if request.method == 'POST':
            # if this was a POST request then grab the data from
            # the forms and structure it so that when you render
            # the form again it reflects the changes made on submit
            self.FACEBOOK_MANAGED_PAGES = []
            d_pages = dict(pages)
            for k, v in d_pages.iteritems():
                if k.startswith('fbookpage_'):
                    self.FACEBOOK_MANAGED_PAGES.append(
                        (v[0], d_pages['business_'+k[-1]][0]))

            for i, page in enumerate(self.FACEBOOK_MANAGED_PAGES):
                page_field = forms.ChoiceField(
                    label   = 'Page Name',
                    choices = [(x[0], x[0]) for x in self.FACEBOOK_MANAGED_PAGES],
                    initial = self.FACEBOOK_MANAGED_PAGES[i][0],
                    widget  = forms.Select(attrs={
                                'class':'fever_field fbook_page_field'}))
                biz_field = forms.ChoiceField(
                    label   = 'Business',
                    choices = self.MANAGED_BIZ_CHOICES,
                    initial = self.FACEBOOK_MANAGED_PAGES[i][1],
                    widget  = forms.Select(attrs={
                                'class':'fever_field managed_biz_field'}))

                self.fields["fbookpage_{}".format(i+1)] = page_field
                self.fields["business_{}".format(i+1)]  = biz_field


        else:
            self.FACEBOOK_MANAGED_PAGES = tuple([
                (x['name'], x['name']) for x in pages])

            for i, page in enumerate(pages):
                page_field = forms.ChoiceField(
                    label   = 'Page Name',
                    choices = self.FACEBOOK_MANAGED_PAGES,
                    initial = self.FACEBOOK_MANAGED_PAGES[i][0],
                    widget  = forms.Select(attrs={
                                'class':'fever_field fbook_page_field'}))
                biz_field = forms.ChoiceField(
                    label   = 'Business',
                    choices = self.MANAGED_BIZ_CHOICES,
                    widget  = forms.Select(attrs={
                                'class':'fever_field managed_biz_field'}))

                self.fields["fbookpage_{}".format(i+1)] = page_field
                self.fields["business_{}".format(i+1)]  = biz_field

    def construct_forms(pages):
        ''' This function takes the POST data as input 
        and saves associations where an associative match is found,
        ignores selections with an empty business field, and
        ignores the pages marked ignore
        '''
        pass

    def clean(self):
        #self.saved_data = self.cleaned_data
        #return self.cleaned_data
        cleaned_data = super(SaveFbookPageForm, self).clean()
        return cleaned_data 

    class Meta:
        model   = FacebookManagedPages
        exclude = ('user', 'biz', 'name', 'category',
                   'fbook_uid', 'perms', 'access_token', 'ignored')


"""
