from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponseForbidden, Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, render, redirect
from myproject.apps.biz.models import Business
from myproject.mixins import SuperuserRequiredMixin, LoginRequiredMixin

#-----------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------

def home(request):
    '''render the home page'''
    context = {
        'STATIC_URL' : settings.STATIC_URL,
        'LOGIN_URL'  : settings.LOGIN_URL,
        'LOGOUT_URL' : settings.LOGOUT_URL
        }
    return render_to_response('homepage.html', context, RequestContext(request))


@login_required(login_url=settings.LOGIN_URL)
def dashboard(request, template_name='dashboard.html'):
    ''' The insightfever main dashboard
    '''
    ctx = {}
    biz_list = Business.objects.filter(members__exact=request.user.id)
    ctx['biz_list']  = biz_list
    ctx['dashboard'] = True

    # generate pagination based on how many business you count
    if biz_list:
        if biz_list.count() > 10:
            ctx['needs_pagination'] = True

    return render_to_response(template_name, ctx, RequestContext(request))


#-----------------------------------------------------------------------------
# TEMPORARY TEST CODE GOES BELOW
#-----------------------------------------------------------------------------

import datetime
from social_auth.models import UserSocialAuth
from django.utils.timezone import utc
from myproject.apps.social.models import PostQueue
from myproject.apps.social.forms import PostQueueForm


class TestView(LoginRequiredMixin, SuperuserRequiredMixin, TemplateView):
    '''View that serves as a sandbox for testing various bits of code
    '''
    template_name = "TEST.html"

    def get(self, request, *args, **kwargs):
        ctx = self.get_context_data(**kwargs)
        ctx['dir']  = str(dir(request))
        ctx['host'] = request.META['HTTP_HOST']

        accounts = UserSocialAuth.objects.filter(user_id=request.user.id)
        if accounts:
            for account in accounts:
                if account.provider == 'facebook':
                    ctx['facebook_disconnect_id'] = account.id

        #TODO
        # Make sure the biz_id variable is dynamically generated when 
        # moving this from the test area into the actual postqueue page

        # upcoming posts formset
        upcoming_posts = PostQueue.objects.filter(biz_id=1
        ).exclude(post_date__lt=datetime.datetime.utcnow().replace(tzinfo=utc)
        ).exclude(status__exact='inactive').order_by('post_date')

        # create a list of of your post forms
        form_list = []
        for post in upcoming_posts:
            form_list.append(PostQueueForm(instance=post))
        ctx['upcoming_posts'] = form_list
        
        return self.render_to_response(ctx)



'''
if request.user.is_staff:
    return HttpResponseRedirect('/admin/')
'''

