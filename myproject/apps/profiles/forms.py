from django import forms
from django.utils.translation import ugettext_lazy as _
from userena.forms import SignupForm

class SignupFormExtra(SignupForm):
    ''' Add custom fields to the signup form
    '''
    first_name = forms.CharField(label=_(u'First name'),  max_length=30, required=False)
    last_name  = forms.CharField(label=_(u'Last name'),   max_length=30, required=False)
    facebook   = forms.CharField(label=_(u'Facebook URL'), required=False, 
                                 help_text=_('* add your facebook username'))
    twitter    = forms.CharField(label=_(u'Twitter URL'),  required=False, 
                                 help_text=_('* add your twitter username'))
    
    def __init__(self, *args, **kw):
        ''' Rearrange form fields to put first and last name at the top 
        '''
        super(SignupFormExtra, self).__init__(*args, **kw)
        new_order = self.fields.keyOrder[:-2]
        new_order.insert(0, 'first_name')
        new_order.insert(1, 'last_name')
        self.fields.keyOrder = new_order
    
    def save(self):
        ''' Override the save method in order to save your added fields
        '''
        # First save the parent form and get the user object. then get profile
        new_user = super(SignupFormExtra, self).save()
        new_user = new_user.get_profile()

        # validate your new fields
        new_user.first_name = self.cleaned_data['first_name']
        new_user.last_name  = self.cleaned_data['last_name']
        new_user.facebook   = self.cleaned_data['facebook']
        new_user.twitter    = self.cleaned_data['twitter']
        new_user.save()
        return new_user

