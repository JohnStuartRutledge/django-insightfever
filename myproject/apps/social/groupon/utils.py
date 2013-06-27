from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from social_auth.models import UserSocialAuth

from myproject.apps.biz.models import Business

#-----------------------------------------------------------------------------
# 
#-----------------------------------------------------------------------------
# Link to Groupon API documentation: link

def connect_to_groupon(user_id, biz_id):
    ''' Connect to Groupon and retrive deals ordered by
    how close they are distance wise to the given business
    '''
    pass