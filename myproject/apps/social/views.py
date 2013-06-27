from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import ProcessFormView
from django.views.generic import View, FormView, TemplateView
from django.core.files.uploadhandler import StopUpload
from django.forms.models import modelformset_factory
from django.utils.dateformat import DateFormat
from django.utils.timezone import utc
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson as json
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.conf import settings
from django.forms import Textarea
from django.http import HttpResponse
from django.core import serializers
from django import forms

import dateutil.parser
from dateutil.relativedelta import relativedelta
import datetime
import collections
import calendar
import logging
import tablib
import time
import csv
import re

from social_auth.models import UserSocialAuth

from myproject.mixins import (SuperuserRequiredMixin, LoginRequiredMixin,
    PermissionRequiredMixin, JSONResponseMixin, AjaxResponseMixin)
from myproject.apps.social.models import (Yelp, YelpSimilar, Apt, AptComments,
    AptRatings, AptReplies, Facebook, FacebookDemographics, PostQueue)
from myproject.apps.biz.models import Business, Website, WebsiteTypes
from myproject.apps.social.forms import UploadForm, PostQueueForm
from myproject.apps.social.twitter.utils import connect_to_tweepy
from myproject import fever_utils
from myproject.apps.social.facebook.utils import Fbook, get_facebook_post_data


log = logging.getLogger(__name__)
now = datetime.datetime.now()


#-----------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------

class UploadView(SuperuserRequiredMixin, FormView):
    ''' View for Admin use only that allows you to insert a JSON file made 
    out of scraped data from Scrapy into the database.
    '''
    form_class    = UploadForm
    template_name = 'social/insertjson.html'
    success_url   = 'social/insertjson/success/'
    is_valid = True

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form       = self.get_form(form_class)
        context    = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, 'social/insertjson.html', context)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form       = UploadForm()
        context    = self.get_context_data(**kwargs)
        f          = request.FILES['file']
        sitetype   = request.POST['file_cat']

        context['form']     = form
        context['filename'] = f.name
        context['sitetype'] = sitetype
        context['filesize'] = f.size

        log.info('='*79)

        def _extractDateFromFile(request, file_name, context):
            ''' Extract the timestamp out of the filename
            TODO
            remove this function and add the timestamp w/in the json file itself
            '''
            rs = re.search(r'\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}', file_name)
            try:
                return datetime.datetime.strptime(
                    rs.group(0), "%Y-%m-%dT%H-%M-%S")
            except (AttributeError, ValueError):
                messages.error(request, 
                    'The timestamp could not be extracted from the filename')
                return render(request, 'social/insertjson.html', context)

        # pass on the form data to the various processing functions
        if sitetype == 'yelp':
            data = json.loads(f.read())
            context['jsondata']  = f.read()
            context['timestamp'] = _extractDateFromFile(request, f.name, context)
            return self.validate_yelp_form(request, data, context)

        if sitetype == 'aptratings':
            data = json.loads(f.read())
            context['jsondata']  = f.read()
            context['timestamp'] = _extractDateFromFile(request, f.name, context)
            return self.validate_aptratings_form(request, data, context)

        if sitetype == 'fbook':
            data = list(csv.DictReader(f, delimiter=','))
            return self.validate_fbook_form(request, data, context)


    def validate_yelp_form(self, request, data, context):
        ''' Check to make sure the JSON is valid using Validictory
        TODO
        check filesize, if its too big, then open via f.chunks()
        '''
        rowlist = [] # list to hold individual rows for insertion to DB
        for d in data:
            # Make sure the business your inserting data for exists in the DB
            try:
                biz_id = Business.objects.get(id=d['biz_id'])
            except Business.DoesNotExist:
                if d['biz_id'] == 0:
                    msg = _("""ERROR: FILE NOT UPLOADED: The Business id was
                    0, AKA the businesses URL in your Django DB does not match
                    up with the actual URL on Yelp. Check the Scrapy logs to
                    see what URL was actually scraped """)
                else:
                    msg = _("""ERROR: FILE NOT UPLOADED: The Business id={0}
                    does not exist in the database.""".format(d['biz_id']))

                messages.error(request, msg)
                return render(request, 'social/insertjson.html', context)

            duplicate_data = Yelp.objects.filter(
                                biz=biz_id, scraped_on=context['timestamp'])
            if duplicate_data:
                msg = _("""ERROR: DUPLICATE ITEM IN DATABASE:
                {0} with field: created_on={1} already exists
                """.format(duplicate_data, str(context['timestamp'])))

                messages.error(request, msg)
                return render(request, 'social/insertjson.html', context)
                #return msg, False, None

            # build a new Yelp object out of the Json contents
            rowlist.append(Yelp(
                created_on=now,
                created_by=request.user,
                biz=biz_id,
                stars=d['stars'],
                review_count=d['review_count'],
                scraped_on=context['timestamp']))


        # TODO
        # convert to bulk insert
        # https://docs.djangoproject.com/en/dev/ref/models/querysets/#bulk-create
        # Yelp.objects.bulk_create(rowlist)
        for row in rowlist:
            row.save()

        log.info('JSON data was inserted to DB')
        messages.info(request, _('Your JSON data is Valid'))
        messages.success(
            request, _('Yelp json data was successfully added to Database'))
        return render(request, 'social/insertjson.html', context)


    def validate_aptratings_form(self, request, data, context):
        ''' Validate apartment ratings data
        '''
        rowlist = []
        msg     = ''
        PROPS   = make_biz_dict('Apartment Ratings') # {biz_URL: biz_id}
        valid   = True

        # get the last comment_id in the DB and add 1 to it so that you can
        # properly predict what id the comment you will insert is
        # TODO
        # this is a shitty hack and can be fixed by fixing Scrapy instead.
        try:
            comment_id = AptComments.objects.all().order_by('-id')[:1][0].id
        except IndexError:
            comment_id = 0

        # Add the data to the database.
        for d in data:
            if d.get('total_overall_rating'):
                rowlist.append(Apt(
                    created_on=now,
                    created_by=request.user,
                    biz_id=d['biz_id'],
                    recommended_by=d['recommended_by'],
                    total_overall_rating=d['total_overall_rating'],
                    overall_parking=d.get('overall_parking'),
                    overall_maintenance=d.get('overall_maintenance'),
                    overall_construction=d.get('overall_construction'),
                    overall_noise=d.get('overall_noise'),
                    overall_grounds=d.get('overall_grounds'),
                    overall_safety=d.get('overall_safety'),
                    overall_office_staff=d.get('overall_office_staff'),
                    scraped_on=context['timestamp']
                    ))

            elif d.get('comment_url'):
                comment_id += 1 
                try:
                    comment_url = re.split(r'-\d{4,7}\.html', d['comment_url'])
                    comment_url = comment_url[0] + '.html'
                    biz_id      = PROPS[comment_url]

                    rowlist.append(AptComments(
                        created_on=now,
                        created_by=request.user,
                        biz_id=biz_id,
                        comment_title=d.get('comment_title'),
                        comment_username=d.get('comment_username'),
                        comment_years_stayed=d.get('comment_years_stayed'),
                        comment_message=d.get('comment_message'),
                        scraped_on=context['timestamp']
                        ))

                    rowlist.append(AptRatings(
                        created_on=now,
                        created_by=request.user,
                        biz_id=biz_id,
                        comment_id=comment_id,
                        overall_rating=d.get('overall_rating'),
                        parking=d.get('parking'),
                        maintenance=d.get('maintenance'),
                        construction=d.get('construction'),
                        noise=d.get('noise'),
                        grounds=d.get('grounds'),
                        safety=d.get('safety'),
                        office_staff=d.get('office_staff'),
                        scraped_on=context['timestamp']
                        ))

                    # check if there are any replies attached to this comment
                    # if there are, add them to the Replies table in the DB
                    if d.get('replies') is not None:

                        for rid in d['replies'].iterkeys():
                            reply = d['replies'][rid]

                            # try parsing the reply date, e.g. 07/12/2012
                            try:
                                reply_date = datetime.datetime.strptime(
                                    reply['reply_date'], '%m/%d/%Y')
                            except:
                                reply_date = None

                            reply_msg = reply.get('reply_msg')

                            # Prep the items for insertion to DB
                            rowlist.append(AptReplies(
                                created_on=now,
                                created_by=request.user,
                                biz_id=biz_id,
                                comment_id=comment_id,
                                reply_number=int(rid),
                                reply_name=reply.get('reply_name'),
                                reply_date=reply_date,
                                reply_msg=reply_msg,
                                scraped_on=context['timestamp']
                                ))

                except KeyError, err:
                    log.error(err)
                    msg = msg + '\nUNABLE TO PARSE URL: {}'.format(
                                                            d['comment_url'])
                    messages.error(request, msg)
                    return render(request, 'social/insertjson.html', context)
            else:
                log.error('An item in your JSON file could not be parsed')
                msg = msg + '\nCOULD NOT PARSE ITEM: {}'.format(d)
                messages.error(request, msg)
                return render(request, 'social/insertjson.html', context)

        messages.info(request, msg)

        # TODO
        # convert to bulk insert
        # https://docs.djangoproject.com/en/dev/ref/models/querysets/#bulk-create
        for row in rowlist:
            row.save()

        log.info('JSON data was inserted to DB')
        messages.success(request, 
            _('Aptratings Json data was successfully added to Database'))
        return render(request, 'social/insertjson.html', context)


    #-------------------------------------------------------------------------
    #
    #-------------------------------------------------------------------------
    def validate_fbook_form(self, request, data, context):
        ''' Validate Facebook Insights Data
        '''
        d = tablib.Dataset()
        PROPS = make_biz_dict('Facebook')
        count = 0
        dupe_count = 0 # for counting duplicate errors in the DB
        age_sex_regex = re.compile(r'[MFU]\.\d{2}(?=-)') # TODO: fix so that UU gets counted
        fbook_demographics_list = []
        fbook_insights_list = []

        # extract the business name from out of the file
        # TODO
        #   THIS APPROACH EXISTS BECAUSE IT'S FOR USE BY ADMINS ONLY, HOWEVER,
        #   THIS IS A BIG SECURITY NO NO; IT'S ALSO JUST SHITTY CODE.
        #   FIX IT SO THAT YOU CAN SELECT YOUR BUSINESS-NAME VIA A SELECT FORM.
        bizname_to_id = {x.biz_name:x.id for x in Business.objects.all()}

        # check existing biz names against the filename to get the biz_id
        for bizname in bizname_to_id.iterkeys():
            if bizname in context['filename']:
                biz_id = bizname_to_id[bizname]

        try:
            # Make sure the business has registered a facebook account on Insight Fever
            if biz_id not in PROPS.itervalues():
                raise forms.ValidationError('The Business you are submiting ' 
                'has not registered a Facebook account with Insight Fever. ' 
                'Please register one and then try submitting your file again.')
        except NameError:
            log.info('biz does not exist')
            msg = "The business name in your file cannot be found in the DB"
            messages.error(request, msg)
            return render(request, 'social/insertjson.html', context)

        for line in data:
            if count == 0:
                # create lookup table to map id #'s to headers
                head_lookup = collections.OrderedDict(enumerate(line.keys()))
                # replace headers w/ index numbers to save space
                d.headers = head_lookup.keys()
                count += 1
            else:
                d.append(line.values())
                count += 1

        # extract the appropriate fields into a Facebook Object, if the field exists.
        # If the value is empty then set default value to 0
        for line in d.dict:
            lifetime_demographics = collections.defaultdict(lambda: 0, {})
            weekly_demographics   = collections.defaultdict(lambda: 0, {})

            # running set() on empty lines should return a value of 3 for date, id, and ''
            # if len is 3+ extract the data, else skip the line b/c its values are empty
            if len(set(line.itervalues())) <= 3:
                break

            for row in head_lookup.iteritems():
                field_id   = row[0]
                field_name = row[1]

                if field_name == 'Date':
                    row_date = datetime.datetime.strptime(line[field_id], "%Y-%m-%d")

                    # Check if the date is alredy in the DB
                    if FacebookDemographics.objects.filter(biz_id=biz_id,
                                            date__exact=row_date).exists():
                        dupe_count += 1
                        break
                        # TODO - make this more efficent by not querying in a loop

                if 'Lifetime The total number of people who have liked your Page' in field_name:
                    lifetime_total_likes = line[field_id]
                elif 'Daily The number of new people who have liked your Page' in field_name:
                    daily_new_page_likes = line[field_id]
                elif 'Daily The number of Unlikes of your Page (Unique Users)' in field_name:
                    daily_page_unlikes = line[field_id]
                elif 'Daily The number of people who are friends with people who liked your Page' in field_name:
                    friends_of_fans = line[field_id]
                elif 'Daily The number of people sharing stories about your page.' in field_name:
                    daily_shared_stories = line[field_id]
                elif 'Weekly The number of people sharing stories about your page.' in field_name:
                    weekly_shared_stories = line[field_id]
                elif '28 Days The number of people sharing stories about your page.' in field_name:
                    monthly_shared_stories = line[field_id]
                elif 'Daily The number of people who engaged with your Page' in field_name:
                    daily_engaged_page = line[field_id]
                elif 'Daily The number of people who have seen any content associated with your Page' in field_name:
                    daily_total_reach = line[field_id]
                elif 'Weekly The number of people who have seen any content associated with your Page' in field_name:
                    weekly_total_reach = line[field_id]
                elif '28 Days The number of people who have seen any content associated with your Page' in field_name:
                    monthly_total_reach = line[field_id]
                elif 'Daily The number of impressions that came from all of your posts' in field_name:
                    daily_post_impressions = line[field_id]
                elif 'Weekly The number of impressions that came from all of your posts' in field_name:
                    weekly_post_impressions = line[field_id]
                elif '28 Days The number of impressions that came from all of your posts' in field_name:
                    monthly_post_impressions = line[field_id]
                elif 'Top referrering external domains sending traffic to your Page' in field_name:
                    # extract domains here
                    pass
                elif 'Lifetime Aggregated Facebook location data, sorted by city' in field_name:
                    # extract cities here
                    pass
                elif 'Weekly Total Page Reach by age and gender' in field_name:
                    # current demographic data about age-sex is here
                    result = re.search(age_sex_regex, field_name)
                    if result:
                        weekly_demographics[result.group().replace('.', '')] = line[field_id]
                elif 'Lifetime Aggregated demographic data' in field_name:
                    # add demographic data about age-sex to fbdemo dictionary
                    result = re.search(age_sex_regex, field_name)
                    if result:
                        lifetime_demographics[result.group().replace('.', '')] = line[field_id]

            else:
                # this else statment only gets executed if the break
                # statement in the above for loop never gets used
                fbook_insights_list.append(Facebook(
                    created_on=now,
                    created_by=request.user,
                    biz_id=biz_id,
                    date=row_date,
                    lifetime_total_likes=lifetime_total_likes,
                    daily_new_page_likes=daily_new_page_likes,
                    daily_page_unlikes=daily_page_unlikes,
                    friends_of_fans=friends_of_fans,
                    daily_shared_stories=daily_shared_stories,
                    weekly_shared_stories=weekly_shared_stories,
                    monthly_shared_stories=monthly_shared_stories,
                    daily_engaged_page=daily_engaged_page,
                    daily_total_reach=daily_total_reach,
                    weekly_total_reach=weekly_total_reach,
                    monthly_total_reach=monthly_total_reach,
                    daily_post_impressions=daily_post_impressions,
                    weekly_post_impressions=weekly_post_impressions,
                    monthly_post_impressions=monthly_post_impressions
                    ))

                fbook_demographics_list.append(FacebookDemographics(
                    created_on=now,
                    created_by=request.user,
                    biz_id=biz_id,
                    date=row_date,
                    M13=lifetime_demographics['M13'],
                    M18=lifetime_demographics['M18'],
                    M25=lifetime_demographics['M25'],
                    M35=lifetime_demographics['M35'],
                    M45=lifetime_demographics['M45'],
                    M55=lifetime_demographics['M55'],
                    F13=lifetime_demographics['F13'],
                    F18=lifetime_demographics['F18'],
                    F25=lifetime_demographics['F25'],
                    F35=lifetime_demographics['F35'],
                    F45=lifetime_demographics['F45'],
                    F55=lifetime_demographics['F55'],
                    U13=lifetime_demographics['U13'],
                    U18=lifetime_demographics['U18'],
                    U25=lifetime_demographics['U25'],
                    U35=lifetime_demographics['U35'],
                    U45=lifetime_demographics['U45'],
                    U55=lifetime_demographics['U55'],
                    UU=lifetime_demographics['UU']
                    ))

        # create the objects
        FacebookDemographics.objects.bulk_create(fbook_demographics_list)
        Facebook.objects.bulk_create(fbook_insights_list)
        messages.success(request, _('Facebook Insights data was successfully submitted'))

        # if duplicates were found - send the user a warning
        if dupe_count > 0:
            messages.warning(request, _('WARNING: {} duplicates were found and \
            omitted from insertion into the database'.format(dupe_count)))

        return render(request, 'social/insertjson.html', context)



class AmenitiesView(LoginRequiredMixin, TemplateView):
    ''' Page for showing useful information to a business. Examples include
    Groupon deals, Walkability score, etc.
        http://code.google.com/p/python-groupon/
        https://sites.google.com/site/grouponapiv2/api-usage

    TODO
    complete this view 
    '''
    template_name="reports/amenities.html"

    # from groupon.resources.deals import Deal
    grouponkey = settings.GROUPON_API_KEY
    # dealInterface = Deal()
    myOptions = {'division':'Austin'}
    # status, deals = dealInterface.get(grouponkey, options=myOptions)
    # print([deal.id for deal in deals])

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['groupon_key'] = grouponkey
        return self.render_to_response(context)


class PostView(LoginRequiredMixin, TemplateView):
    ''' View for scheduling and posting to Facebook and Twitter
    either individually, or simultaniously
    '''
    template_name="social/post_queue.html"

    def get_context_data(self, **kwargs):
        ctx = super(PostView, self).get_context_data(**kwargs)
        ctx['biz'] = get_object_or_404(Business, pk=self.kwargs['biz_id'])
        return ctx

    def get(self, request, *args, **kwargs):
        ctx = self.get_context_data(**kwargs)
        ctx['form'] = PostQueueForm(initial={'status': 'active',
                                       'social_sites': [u'facebook']})
        ctx['biz_list'] = fever_utils.get_user_businesses(request.user)
        user_biz_ids = [x.id for x in ctx['biz_list'] if ctx['biz_list']]

        # get all posts that are scheduled for future deployment
        upcoming_posts = PostQueue.objects.filter(biz_id__in=user_biz_ids
        ).exclude(post_date__lt=datetime.datetime.utcnow().replace(tzinfo=utc)
        ).exclude(status__exact='draft').order_by('post_date')

        # create a list of of your post forms
        form_list = []
        for post in upcoming_posts:
            form = PostQueueForm(instance=post)
            #form.fields['social_sites'].initial = post.social_sites
            form.fields['social_sites'].initial = u'Facebook'
            form_list.append(form)
        ctx['upcoming_posts'] = form_list

        # get all saved drafts
        ctx['drafts'] = [PostQueueForm(instance=draft) for draft in \
            PostQueue.objects.filter(
                biz_id__in=user_biz_ids, status__exact='draft')]

        # get all posts that have already been sent
        ctx['past_posts'] = PostQueue.objects.filter(
            biz_id=self.kwargs['biz_id']).exclude(
                post_date__gt=datetime.datetime.now()).order_by('-post_date')

        # check if connected to facebook and if not then display
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

        if form.is_valid():
            params = {}

            # add the missing values for created_by and created_on since
            # modelForms seem to have trouble automaticlly inheriting them
            the_post = form.save(commit=False)
            the_post.created_by = request.user
            the_post.created_on = datetime.datetime.utcnow().replace(tzinfo=utc)
            params['message'] = the_post.message

            # check which social networks they specified and configure the
            # parameters for your API request accordingly
            if 'facebook' in the_post.social_sites:
                fb = Fbook(user_id=request.user.id)

                # confirm that the messages in the insightfever DB matches
                # those scheduled on Facebook. If a descrepancy is found
                # then update either facebook or your own DB appropriately
                facebook_posts = fb.sync_managed_posts(the_post.biz_id)
                data = facebook_posts['data']
                for d in data:
                    log.info(d)
                    # TODO
                    # convert the unix timestamp in d['created_time'] to
                    # a datetime object and figure out if the message has
                    # already been posted yet. If a time descrepancy is found
                    # then prompt the user with a dialogue box asking if they
                    # want to overwrite the insightfever data with the facebook
                    # or if they want to overwrite facebook data with ifever.
                    # d['source_id']
                    # d['post_id']
                    # d['created_time']
                    # d['message']

                # search the message for links. If found then request the page
                # for your first URL and search for facebook metatags so that
                # you can autofill some of the required fields:
                urls = fever_utils.find_urls(the_post.message)
                if urls:
                    # TODO:
                    # grab the link parameters from the javascript in the
                    # page. AKA, create some hidden forms from which to
                    # store your retrived javascript values, and on submit
                    # to Facebook, inject those values into the API call
                    params['link'] = urls[0]
                    params = fb.getLinkParams(params)

                params['scheduled_publish_time'] = the_post.post_date

                # Post your message to the facebook page
                result = fb.postToPage(request, params, the_post.biz_id)

                # make sure Facebook acknowledged our post by returning an id
                if 'id' in result:
                    the_post.fbook_post_id = result['id']
                else:
                    msg = "Facebook failed to return a post 'id'. You message failed to post"
                    log.error(msg)
                    message.error(request, msg)

            # if they chose to post to Twitter
            if 'twitter' in the_post.social_sites:
                # twit = connect_to_tweepy(request.user.id, the_post.biz_id)
                # NOTE 
                # if posting a picture you need to use the
                # update_with_media parameter
                # https://dev.twitter.com/docs/api/1.1/post/statuses/update_with_media
                pass

            the_post.save()

            messages.info(request, 'Your post has been scheduled')
            return HttpResponseRedirect(reverse('social_post',
                                    args=(self.kwargs['biz_id'],)))

        messages.error(request, 'Your form did not validate')
        return self.render_to_response(ctx)


class FacebookJsonResponse(LoginRequiredMixin, JSONResponseMixin, TemplateView):
    ''' Takes the URL from an AJAX request on the PostQueue page, queries the 
    URL for data, and constructs some HTML from it. It then returns the fully 
    rendered HTML in a JSON object which Jquery then injects into the page.
    '''
    def get(self, request, *args, **kwargs):
        # TODO
        # move the html elements to your themes folder
        ctx = self.get_context_data(**kwargs)
        url = request.GET.get('url', '')
        if url:
            rs = get_facebook_post_data(url)
            if 'link' in rs:
                # TODO - truncate the link
                link = "<div id='fbook_subtitle'>{0}</div>".format(rs['link'])
            else:
                link = ""

            if 'picture' in rs:
                # check if there are one or many pictures included
                # if there are many then construct the pagenator
                pictures = """\
                <div id='fbook_image'>
                    <div id='fbook_img_pager'>
                        <div id='fbook_img_loader'>
                            <img id='fbook_loading_img' src='imgsrc' width='16' height='11'>
                        </div>
                        <div id='fbook_thumbs'>
                            <img src='{0}' class='fbook_thumb' id='fbook_thumb_1'>
                        </div>
                    </div>
                </div>""".format(rs['picture'])

                pic_paginator = """\
                <div id='fbook_thumbnail_pager'>
                    <div id='fbook_pager_control_buttons'>
                        <a id='fbook_pager_left_btn'></a>
                        <a id='fbook_pager_right_btn'></a>
                    </div>
                    <div id='fbook_pager_text'>
                        <span id='fbook_pager_number'>
                            <span id='fbook_pg_current'></span>
                             of
                            <span id='fbook_pg_total'></span>
                        </span>
                        Choose a Thumbnail
                    </div>
                    <div id='fbook_nothumb_wrapper'>
                        <input id='fbook_nothumb_checkbox' type='checkbox' value='true' name='no_picture'>
                        <label for='fbook_nothumb_checkbox'>No Thumbnail</label>
                    </div>
                </div>
                """

                # temporarily leave paginator blank
                pic_paginator = ""
            else:
                pictures = ""
                pic_paginator = ""

            # NAME
            if 'name' in rs:
                title = "<div id='fbook_title'>{0}</div>".format(rs['name'])
            else:
                title = ""

            # DESCRIPTION
            if 'description' in rs:
                description = """\
                <div id='fbook_summary'>
                    <p id='fbook_description'><a onclick='InlineEdit(this)'>{0}</a></p>
                </div>
                """.format(rs['description'])
            else:
                description = ""

            # put the HTML all together
            html_output = """\
            <div id='fbook_content_wrapper'>
                {pictures}
                {title}
                {link}
                {description}
                {pic_paginator}
            </div>
            """.format(title=title, link=link, pictures=pictures,
                description=description, pic_paginator=pic_paginator)

            ctx['html_output'] = html_output
        else:
            ctx['html_output'] = 'fail'
        return self.render_json_response(ctx)

    def post(self, request, *args, **kwargs):
        ctx = self.get_context_data(**kwargs)
        ctx['url'] = request.POST.get('url', 'fail')
        return HttpResponse(serializers.serialize('json', result),
                                        mimetype="application/json")

class EditAjaxPostView(JSONResponseMixin, AjaxResponseMixin, View):
    ''' Takes the URL from an AJAX request on the PostQueue page,
    queries the url for data, and constructs some HTML out of that data.
    It then returns the fully rendered HTML in a JSON object which
    Jquery then injects into the page.
    ProcessFormView
    '''
    def post_ajax(self, request, *args, **kwargs):
        # TODO 
        # in fact this whole approach is a disgrace. Figure out how
        # to use Djangos modelformsets with AJAX and save things properly
        # to start with you should inherit from some view that has the
        # get_context_data method, then use that to pull some info
        ctx = {}

        # extract the forms id from out the dictionaries keys
        for x in request.POST.items():
            if x[0].endswith('-id'):
                form_id = int(x[0][-4]) # id of form on html page

        # extract the values from the submitted form and create a
        # new dictionary out of it that is actually usuable
        prefix = "form-{}-".format(form_id)
        form = {}
        for x in request.POST.items():
            if prefix in x[0]:
                left, right = x[0].split(prefix)
                form[right] = x[1]
            else:
                form[x[0]] = x[1]

        # query the DB to get the form in question
        post = PostQueue.objects.get(id=form['id'])

        # figure out which button they pressed (save, deactivate, or delete)
        # and perform different actions in response
        if form['btn_type'] in ('delete', 'draft'):
            # TODO
            # update facebook via the API. Note: the fbook_post_id will
            # need to be deleted for those posts that are now marked
            # as a draft
            fb = Fbook(user_id=request.user.id)
            draft = True if form['btn_type'] == 'draft' else False
            post_error = fb.deletePost(request, post.fbook_post_id, draft)
            if post_error:
                ctx['msg'] = 'your post was successfully deleted'
                return self.render_json_response(ctx)
            else:
                ctx['msg'] = 'An error occurred and we were unable to delete your post'
                return self.render_json_response(ctx)

        if form['btn_type'] == 'draft':
            post.status = 'draft'
            # TODO
            # write code here that sends a delete request to
            # facebook like is done above, only this time alter the
            # local copy of the post to be a draft.

        # TODO
        # check to see if there were any changes made to the form on save
        # If no changes were made then do not send Facebook an API request
        # to modify your message. If changes were made then send the request.
        # Note that if Facebook returns an error then do not resave this form.
        # code goes here

        # check if the item has an existing fbook_post_id.
        # if it does then this means they are updating/rescheduling a post

        # update the posts fields with the submitted information
        post.biz_id     = form['biz']
        post.message    = form['message']
        post.updated_by = request.user
        post.updated_on = datetime.datetime.utcnow().replace(tzinfo=utc)

        # construct the new date
        ptime = '{} {}:{}{}'.format(
            form['post_date_0'],
            form['post_date_1'],
            form['post_date_2'],
            form['post_date_3'])
        post.post_date = dateutil.parser.parse(ptime)

        # TODO
        # find a way to get the social site info
        # post.social_sites = [u'facebook']

        post.save()

        # TODO - load the given post for the submitted post id
        #        AKA only load a post when the user request it
        #        VS what your doing right now which is loading
        #        all the posts and just hiding them with AJAX
        ctx['hi']  = form['id']
        ctx['msg'] = 'your post was saved successfully'

        return self.render_json_response(ctx)




class AccountsView(LoginRequiredMixin, TemplateView):
    ''' View for displaying and logging in to Social Media accounts
    '''
    template_name ="social/accounts.html"
    #template_name = "biz/biz_accounts.html"

    def get(self, request, *args, **kwargs):
        ctx = {}
        # check to see which 3rd party social sites have already been added
        # by this user, and set template variables to display existing connections.
        accounts = UserSocialAuth.objects.filter(user_id=request.user.id)

        if accounts:
            for account in accounts:
                if account.provider == 'google-oauth2':
                    ctx['google_disconnect_id'] = account.id
                elif account.provider == 'facebook':
                    ctx['facebook_disconnect_id'] = account.id
                elif account.provider == 'twitter':
                    ctx['twitter_disconnect_id'] = account.id
                else:
                    messages.error(request, _('ERROR: Unknown Provider'))
        return self.render_to_response(ctx)





class SettingsView(LoginRequiredMixin, TemplateView):
    ''' View for displaying and editing your social media settings
    '''
    template_name ="social/settings.html"

    def get(self, request, *args, **kwargs):
        ctx = {}
        ctx['settings'] = 'test'
        return self.render_to_response(ctx)


#-----------------------------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------------------------


def make_biz_dict(site_type):
    '''
    Takes the name of the site your scraping (e.g, Yelp, Facebook) and
    returns a dictionary of URLs to scrape along with their matching biz id
    EXAMPLE OUTPUT (key=url, val=biz.id):
    {u'http://www.apartmentratings.com/<APT-URL>.html': 3, }
    '''
    # create the list of websites to scrape by querying Django DB
    # example site_type's are: 'Yelp', 'Apartment Ratings', 'Twitter'
    website_id = WebsiteTypes.objects.get(site_type=site_type).id
    results    = Website.objects.values('business', 'site_url').filter(
                                                     site_type=website_id)

    if results:
        return { x['site_url']: x['business'] for x in results if x['site_url'] }
    return None





