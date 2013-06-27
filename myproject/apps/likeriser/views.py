from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import modelformset_factory
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from social_auth.models import UserSocialAuth
from guardian.shortcuts import get_perms

import tweepy
import json
import logging
from datetime import datetime

from myproject.mixins import LoginRequiredMixin, PermissionRequiredMixin
from myproject.apps.likeriser.forms import PostQueueForm
from myproject.apps.biz.models import Business
from myproject.fever_utils import get_user_businesses
from myproject.apps.social.posts.models import PostQueue
from myproject.apps.social.twitter.utils import connect_to_tweepy

log = logging.getLogger(__name__)

#-----------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------


class LikeriserView(LoginRequiredMixin, TemplateView):
    ''' Page for viewing likeriser data for a particular business.
    '''
    template_name="likeriser/likeriser.html"

    def get_context_data(self, **kwargs):
        ctx = super(LikeriserView, self).get_context_data(**kwargs)
        ctx['biz'] = get_object_or_404(Business, pk=self.kwargs['biz_id']) 
        return ctx

    def get(self, request, *args, **kwargs):
        ctx = {}
        ctx['form'] = PostQueueForm(initial={
                        'status': 'active', 
                        'social_sites': [u'facebook']}
                        )
        ctx['biz_list'] = get_user_businesses(request.user)

        # get all posts that are scheduled for future deployment
        upcoming_posts = PostQueue.objects.filter(
            biz_id=self.kwargs['biz_id']).exclude(
                post_date__lt=datetime.now()).order_by('post_date')

        # get all posts that have already been sent
        past_posts = PostQueue.objects.filter(
            biz_id=self.kwargs['biz_id']).exclude(
                post_date__gt=datetime.now()).order_by('-post_date')
        
        # make a formset out of the upcoming posts
        PostFormSet = modelformset_factory(PostQueue, 
            form=PostQueueForm, extra=0)

        UpcomingFormSet = PostFormSet(queryset=upcoming_posts)

        ctx['upcoming_formset'] = UpcomingFormSet
        ctx['upcoming_posts']   = upcoming_posts
        ctx['past_posts']       = past_posts

        # check if connected to facebook. If not, then display
        # a link to the accounts page to connect to it
        accounts = UserSocialAuth.objects.filter(user_id=request.user.id)
        if accounts:
            for account in accounts:
                if account.provider == 'facebook':
                    ctx['facebook_disconnect_id'] = account.id
                elif account.provider == 'twitter':
                    ctx['twitter_disconnect_id'] = account.id
        return self.render_to_response(ctx)

    def post(self, request, *args, **kwargs):
        ctx = self.get_context_data(**kwargs)
        form = PostQueueForm(request.POST or None)
        ctx['form'] = form

        # if twitter account exists, connect to Twitter
        api = connect_to_tweepy(request.user.id, self.kwargs['biz_id'])

        if form.is_valid():
            # add the missing values for created_by and created_on since
            # modelForms seem to have trouble automaticlly inheriting them
            the_post = form.save(commit=False)
            the_post.created_by = request.user
            the_post.created_on = datetime.now() 
            the_post.biz_id     = self.kwargs['biz_id'] # TODO: remove this 
            the_post.save()

            # see signals.py for adding this saved post to
            # the Celery queue via the post_save signal
            
            messages.info(request, 'Your post has been scheduled')
            return HttpResponseRedirect(reverse('likeriser_view', 
                                    args=(self.kwargs['biz_id'],)))

        messages.error(request, 'Your form did not validate')
        return self.render_to_response(ctx)

    def post_to_twitter(self, request, biz_id, msg):
        ''' Posts to Twitter wall
        TODO
        if connection to twitter fails, set a flag for the post
        that lets the user know the details of why it failed.
        '''
        api = connect_to_tweepy(request.user.id, biz_id)
        update = api.update_status(msg)
        return update.text

    def post_to_facebook(self, request, biz_id):
        ''' Posts to Facebook wall
        '''
        # get the message you want to post
        msg = request.POST.get('message')

        # TODO
        # post your message to facebook


def get_user_avatar(backend, details, response, 
                    social_user, uid, user, *args, **kwargs):
    ''' Example of using django-social-auth to create a pipeline for 
    grabbing a users avatar. 
    http://tryolabs.com/Blog/2012/02/13/get-user-data-using-django-social-auth/ 

    make sure to add the following line to your SOCIAL_AUTH_PIPELINE
        'auth_pipelines.pipelines.get_user_avatar',
    '''
    url = None
    if backend.__class__ == FacebookBackend:
        url = "http://graph.facebook.com/%s/picture?type=large" % response['id']
    elif backend.__class__ == TwitterBackend:
        url = response.get('profile_image_url', '').replace('_normal', '')
 
    if url:
        profile = user.get_profile()
        avatar  = urlopen(url).read()
        fout    = open(filepath, "wb") #filepath is where to save the image
        fout.write(avatar)
        fout.close()
        profile.photo = url_to_image # depends on where you saved it
        profile.save()


#-----------------------------------------------------------------------------
# 
#-----------------------------------------------------------------------------
# TODO 
# make sure that hitting the forms save button does not effect the formsets
# content and vise versa

"""
# EXAMPLES OF POSTING VIA THE FACEBOOK GRAPH API

@facebook_required(scope='publish_actions')
def open_graph_beta(request):
    ''' simple example on how to post to via the open graph api
    '''
    fb = get_persistent_graph(request)
    # post the action 'love' to the users timeline with the object
    # data found at the url stored in entity_url
    entity_url = 'http://www.insightfever.com/item/2081202/'
    result = fb.set('me/insightfever:love', item=entity_url)
    messages.info(request, 'The item has been shared to insightfever:love')


@task.task(ignore_result=True)
def open_graph_beta(user):
    ''' Example posting to open graph using a celery task
    '''
    profile    = user.get_profile()
    fb         = profile.get_offline_graph()
    entity_url = 'http://www.insightfever.com/item/2081202/'
    result     = fb.set('me/insightfever:love', item=entity_url)


@facebook_required(scope='publish_stream')
def wall_post(request):
    ''' Write the input of a form to someones wall
    '''
    fb = get_persistent_graph(request)
    msg = request.POST.get('message')
    fb.set('me/feed', message=msg)
    messages.info(request, 'Posted the message to your wall')
    return next_redirect(request)
"""
