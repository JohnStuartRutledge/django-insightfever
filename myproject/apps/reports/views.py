from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.decorators import method_decorator
from django.forms.models import modelformset_factory, inlineformset_factory
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Max
from django.utils import html

from social_auth.models import UserSocialAuth
from guardian.shortcuts import get_perms

# from myproject.apps.reports.models import Reports
from myproject.mixins import LoginRequiredMixin, PermissionRequiredMixin
from myproject.apps.biz.models import Business, WebsiteTypes, Website
from myproject.fever_utils import getBiz, get_user_businesses

from myproject.apps.social.models import (Facebook, FacebookDemographics,
    Yelp, YelpSimilar, Apt, AptComments, AptRatings, AptReplies)
from myproject.apps.social.facebook.utils import make_url, handle_fbook_errors
from myproject.apps.social.twitter.utils import connect_to_tweepy
from myproject.apps.social.facebook.forms import FbookPageForm
from myproject.apps.social.facebook.models import FacebookManagedPages

import json
import logging
import requests
import mailchimp
from mailchimp.exceptions import MCListDoesNotExist


_parse_json = lambda s: json.loads(s)
log = logging.getLogger(__name__)

#-----------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------

# TODO
# fill out the functions for use in the case statement

def get_homepg_data(ctx):
    ctx['homepg_data'] = 'EMPTY'

def get_blog_data(ctx):
    ctx['blog_data'] = 'EMPTY'

def get_twitter_data(ctx):
    ctx['twitter_data'] = 'EMPTY'

def get_youtube_data(ctx):
    ctx['youtube_data'] = 'EMPTY'

def get_yelp_data(ctx):
    yelp_data = Yelp.objects.filter(biz=ctx['biz_id']).order_by('-created_on')
    ctx['yelp_data'] = yelp_data if yelp_data else 'EMPTY'

def get_facebook_data(ctx):
    ctx['fbook_data'] = Facebook.objects.filter(
                            biz=ctx['biz_id']).order_by('-created_on')
    try:
        fb = FacebookDemographics.objects.filter(
                            biz=ctx['biz_id']).latest('date')
        if fb:
            ctx['fbook_demo'] = json.dumps({
                "M.13-17": fb.M13, "F.13-17": fb.F13, "U.13-17": fb.U13,
                "M.18-24": fb.M18, "F.18-24": fb.F18, "U.18-24": fb.U18,
                "M.25-24": fb.M25, "F.25-34": fb.F25, "U.25-34": fb.U25,
                "M.35-34": fb.M35, "F.35-44": fb.F35, "U.35-44": fb.U35,
                "M.45-54": fb.M45, "F.45-54": fb.F45, "U.45-54": fb.U45,
                "M.55+":   fb.M55, "F.55+":   fb.F55, "U.55+":   fb.U55,
                "U.UNKNOWN": fb.UU
                })
    except FacebookDemographics.DoesNotExist:
        pass

def get_aptratings_data(ctx):
    # Dump a JSON object containing all the apartment ratings data
    # for a particular business. To be used in d3.js chart
    aptdata = Apt.objects.filter(
                        biz=ctx['biz_id']).order_by('-created_on').values()
    if aptdata:
        ctx['aptratings_data'] = aptdata
        apt_json = list(aptdata)
        # for security reasons, delete the following fields
        for i, x in enumerate(apt_json):
            del(apt_json[i]['biz_id'])
            del(apt_json[i]['created_by_id'])
            del(apt_json[i]['updated_by_id'])
            del(apt_json[i]['updated_on'])

        ctx['aptratings_json'] = json.dumps(apt_json, cls=DjangoJSONEncoder)



class Overview(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    ''' Returns the report-overview data relevant to the current user
    '''
    template_name       = "reports/overview.html"
    permission_required = 'biz.view_business'

    def get(self, request, *args, **kwargs):
        biz_id = self.kwargs['biz_id']
        biz    = get_object_or_404(Business, pk=biz_id)
        ctx    = {'biz': biz, 'biz_id': biz_id}

        case = {
            1: get_homepg_data,
            2: get_blog_data,
            3: get_facebook_data,
            4: get_twitter_data,
            5: get_yelp_data,
            6: get_youtube_data,
            7: get_aptratings_data,
            }

        # get the relevant data for each of this businesses active sites
        for active_site in biz.tracked_sites()['active']:
            case[active_site](ctx)
        return self.render_to_response(ctx)


class Social(LoginRequiredMixin, TemplateView):
    ''' InsightFever Social page. Including information
    taken from social sites like Facebook, and Twitter.
    '''
    template_name="reports/social/social.html"
    def get(self, request, *args, **kwargs):
        ctx = {}
        return self.render_to_response(ctx)


class Ratings(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    '''InsightFever Ratings page. Includes info taken 
    from ratings sites like Yelp and Apartmentratings
    TODO - this is a placeholder function
    '''
    # template_name="reports/ratings.html"
    template_name="fever_test.html"
    permission_required = 'biz.view_business'

    def get(self, request, *args, **kwargs):
        ctx = getbiz_details(self.kwargs['biz_id'])
        if request.user.has_perm('biz.view_business'):
            pass
        if request.user.has_perm('social.View_Yelp'):
            pass
        if request.user.has_perm('social.View_Aptratings'):
            pass

        if 'View_Yelp' in get_perms(request.user, Yelp):
            # TODO
            # fix the Django Guardian permissions
            log.info('Django Guardian get_perms(user, Yelp) is working')

        userperms = request.user.get_all_permissions()
        ctx['test'] = repr(ctx)
        return self.render_to_response(ctx)


class Competition(LoginRequiredMixin, TemplateView):
    ''' InsightFever Competition page. 
    TODO - this is a placeholder function
    '''
    #template_name="reports/competition.html"
    template_name="fever_test.html"
    def get(self, request, *args, **kwargs):
        ctx = {}
        return self.render_to_response(ctx)


class TwitterView(LoginRequiredMixin, TemplateView):
    '''Twitter-centric, main page
    '''
    template_name="reports/social/twitter.html"
    def get(self, request, *args, **kwargs):
        # request.session['next'] = request.META['HTTP_REFERER']
        api = connect_to_tweepy(request.user.id, self.kwargs['biz_id'])
        ctx = { 'me': api.me() }
        return self.render_to_response(ctx)


class FacebookView(LoginRequiredMixin, TemplateView):
    ''' Facebook-centric page
    '''
    template_name="reports/social/facebook_formset.html"

    def get(self, request, *args, **kwargs):
        ctx = {}

        # get Facebook access token for the given user
        user_social = UserSocialAuth.objects.get(
                        user_id=request.user.id, provider="facebook")

        # extract the token information and other info
        ACCESS_TOKEN  = user_social.extra_data['access_token']
        TOKEN_EXPIRES = user_social.extra_data['expires']
        FACEBOOK_UID  = user_social.extra_data['id']

        managed_accounts = make_url(
                    "me/accounts", {'access_token': ACCESS_TOKEN})

        # send your request to Facebook
        r = requests.get(managed_accounts)
        handle_fbook_errors(request, r.json)

        # if facebook denies us it's because our session expired.
        # this creates a link to refresh our token in the /accounts section
        # TODO
        # programmatically refresh the app token on error
        if r.status_code == 400:
            ctx['session_expired'] = True
            return render(request, self.template_name, ctx)

        # save facebook JSON response into a variable
        fb_data = r.json

        # make a generator obj full of dicts containing both the original
        # JSON response and the Django DB obj that response should create
        page_objs = ({
            'obj':FacebookManagedPages(user_id=request.user.id, name=x['name'],
                   category=x['category'], fbook_uid=x['id'], perms=x['perms'],
                   access_token=x['access_token'], ignored=False),
            'json':x
        } for x in fb_data['data'] if x['category'] != 'Application')

        # save new managed pages to the DB, ignore existing pages
        # Make this block of code query facebook and then update
        # based on data that has changed
        for page in page_objs:
            try:
                rs = FacebookManagedPages.objects.get(
                        user_id   = request.user.id,
                        name      = page['json']['name'],
                        fbook_uid = page['json']['id'])

                # update the permissions field in case it changed
                rs.perms = page['json']['perms']
                rs.access_token = page['json']['access_token']
                rs.save()

            except FacebookManagedPages.DoesNotExist:
                page['obj'].save()

        # Begin construction of the Formset for associating
        # a users managed facebook pages to Businesses
        PagesFormSet = inlineformset_factory(
            User, FacebookManagedPages, fk_name="user", form=FbookPageForm,
            exclude=FbookPageForm.Meta.exclude, extra=0, can_delete=False)

        # only render forms whose ignore value has never been set
        self.not_ignored = FacebookManagedPages.objects.filter(
            user_id=request.user.id, ignored=False)

        # get the requesting user's User object and insert it into
        # the 'instance' variable so the formset will know to grab
        # only those DB entries associated with the proper user id
        pg_user = User.objects.get(pk=request.user.id)
        ctx['formset'] = PagesFormSet(
            instance=pg_user, prefix='fbook', queryset=self.not_ignored)

        # TODO
        # move most of this functionality into an account settings page

        # TODO
        # create a way to undo the ignored facebook pages feature.
        # as it stands now, if you set a page to be ignored, then
        # you will never see that page show up on the form again

        # TODO
        # don't render the facebook page "name" field as an input,
        # instead you should render the name in a div.
        return self.render_to_response(ctx)


    def post(self, request, *args, **kwargs):
        ctx = self.get_context_data(**kwargs)
        PagesFormSet = inlineformset_factory(
            User, FacebookManagedPages, fk_name="user", form=FbookPageForm,
            exclude=FbookPageForm.Meta.exclude, extra=0, can_delete=False)
        pg_user = User.objects.get(pk=request.user.id)
        formset = PagesFormSet(
            request.POST, request.FILES, instance=pg_user, prefix='fbook')

        if formset.is_valid():
            ctx['formset'] = formset

            # Iterate over instances of the form and save individually.
            # For some reason this prevents a validation error that
            # occurs when just calling formset.save() by itself
            instances = formset.save(commit=False)
            for instance in instances:
                instance.save()
            messages.success(request, 'Your information was saved.')

            # TODO
            # when the user saves a new message form, use some means
            # (e.g, signals) to add the date they entered to the celery
            # scheduled task queue.
        return self.render_to_response(ctx)



class MailchimpView(LoginRequiredMixin, TemplateView):
    ''' Mailchimp-centric page
    TODO
    consider using Banana-Py plugin for django
    https://github.com/kennethlove/Banana-Py
    '''
    template_name="reports/social/mailchimp.html"
    def get(self, request, *args, **kwargs):
        ctx = {}
        # Run test to make sure the mailchimp plugin is working 
        try:
            email_list = mailchimp.utils.get_connection().get_list_by_id('0718f6373c')
        except MCListDoesNotExist:
            email_list = 'DOES NOT EXIST'
        #email_list.subscribe('example@example.com',
        #                    {'EMAIL':'example@example.com'})
        ctx['email_list'] = email_list
        return self.render_to_response(ctx)


#-----------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------

