from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.conf import settings

from social_auth.models import UserSocialAuth
from social_auth.views import auth, complete, disconnect
from social_auth.models import UserSocialAuth

from myproject.apps.social.models import PostQueue, FacebookManagedPages

from BeautifulSoup import BeautifulSoup
import time
import datetime
from dateutil.relativedelta import relativedelta
import urllib
import urlparse
import re
import json
import requests
import logging

log = logging.getLogger(__name__)


#-----------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------
# Facebook documentation at:

"""
TODO:
    cache results and limit queries to Facebook servers

    you must disable sandbox mode on developers.facebook.com
    in order for businesses to start using your app
"""

class FacebookException(Exception):
    def __init__(self, result):
        self.result = result
    def __str__(self):
        return self.__class__.__name__ + ': ' + json.dumps(self.result)


#-----------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------


# define global URLS
AUTHORIZATION_URL  = 'https://www.facebook.com/dialog/oauth'
FACEBOOK_GRAPH_URL = 'https://graph.facebook.com'
ACCESS_TOKEN_URL   = FACEBOOK_GRAPH_URL + '/oauth/access_token'
FACEBOOK_ME_URL    = FACEBOOK_GRAPH_URL + '/me'

class Fbook(object):
    '''
    Class for connecting to the Facebook API
    '''
    def __init__(self, user_id):
        self.user_id = user_id
        try:
            user_social = UserSocialAuth.objects.get(
                user_id=user_id, provider="facebook")
            self.access_token     = user_social.extra_data['access_token']
            self.facebook_id      = user_social.extra_data['id']
            self.token_expiration = user_social.extra_data['expires']

        except UserSocialAuth.DoesNotExist:
            raise 'ERROR'

    def make_url(self, path, params=None):
        ''' Generate urls for posting to Facebook
        '''
        params = params if params else {}
        return '{0}/{1}?{2}'.format(
            FACEBOOK_GRAPH_URL, path, urllib.urlencode(params))

    def _sanitize_params(self, params):
        ''' Set your default URL parameters, sanitize the parameters
        in case you plan to do a POST operation
        '''
        params = params if params else {}

        for key in params:
            if type(params[key]) in [list, dict]:
                params[key] = json.dumps(params[key])
        params.setdefault('access_token', self.access_token)
        return params

    def get(self, path=None, params=None, url=None):
        '''Make a GET request to the Facebook API
        get('oauth/access_token', params=params)
        '''
        if not path and not url:
            raise Exception("you need to specify a path or URL")
        if url:
            result = requests.get(url, params=params)
        else:
            result = requests.get(self.make_url(path, params))
        return result

    def getJson(self, path, params=None, url=None):
        '''Make a get request that returns a JSON object
        '''
        if url:
            rs = requests.get(url, params=params).json
        else:
            rs = requests.get(self.make_url(path, params)).json
        self._handleErrors(rs)
        return rs

    def get_FQL(self, fql, page_token):
        params = {'q':fql}
        if page_token:
            params.update({'access_token': page_token})
        return 'https://graph.facebook.com/fql?' + urllib.urlencode(params)


    #-----------------------------------------------------------------------------
    # MANAGED PAGES FUNCTIONS
    #-----------------------------------------------------------------------------

    def postToPage(self, request, params, biz_id=None):
        ''' Post to a managed pages page. must be a POST request
        DOCS:
            https://developers.facebook.com/docs/reference/api/page/#statues

        params = {
            'message'    : 'your message',        # message or link
            'link'       : 'post URL',            # message or link
            'picture'    : 'post thumbnail img',  # optional; requires link
            'name'       : 'post name',           # optional; requires link
            'caption'    : 'post caption',        # optional; requires link
            'description': 'post description',    # optional; requires link
            'actions'    : 'array of objs',       # optional
            'targeting'  : 'see docs',            # optional
            'published'  : 'boolean',             # optional
            'scheduled_publish_time': 'timestamp' # optional
            }

        /PAGE_ID/feed?
        message
        '''
        # params taken from message submission form
        if not params:
            params = {}
        try:
            # set the access_token and page id to the managed page
            page = FacebookManagedPages.objects.get(
                    user_id=self.user_id, biz_id=biz_id, ignored=0)
            params['access_token'] = page.access_token
            path = '/{}/feed'.format(page.fbook_uid)

            # if scheduled publish time is greater than timedelta(10 minutes)
            # then activate Facebooks scheduled post feature. Note: that if
            # the publish_time falls within the next 10 minutes then the
            # published parameter will default to true and publish immediately
            now = datetime.datetime.now()
            publish_time = params['scheduled_publish_time']
            if publish_time > now+datetime.timedelta(minutes=10):
                params['published'] = False
            params['scheduled_publish_time'] = time.mktime(publish_time.timetuple())

            # send request to facebook and handle errors
            r = requests.post(self.make_url(path, params))
            response = r.json
            self._handleErrors(request, response)
            return response

        except FacebookManagedPages.DoesNotExist:
            messages.error(request, 'The Managed Page does not exist in the db')
            return {}

    def deletePost(self, request, fbook_post_id, draft=False):
        ''' Delete a scheduled post via the facebook API
        '''
        params = {'method':'delete'}
        params['access_token'] = self.access_token
        r = requests.post(self.make_url(fbook_post_id, params))
        response = r.json
        post = PostQueue.objects.get(fbook_post_id=fbook_post_id)
        if response is False:
            log.info('error was found in response')
            log.error('failed to post to facebook: fbook_post_id = {}'.format(
                fbook_post_id))
            return False

        if draft == True:
            post.status = 'draft'
            post.updated_by = request.user
            post.updated_on = datetime.datetime.now()
            post.save()
            log.info('post id={} just changed to a draft'.format(fbook_post_id))
        else:
            post.delete()
            log.info('post id={} was just deleted'.format(fbook_post_id))

        return True

    def getLinkParams(self, params):
        ''' Searches a url for Facebook meta tags. If none found
        Then it searches for information it can use to fill the
        following parameters: picture, name, caption, description.
        META TAG EXAMPLES:
            <meta property="og:title" content="x"/>
            <meta property="og:type" content="x"/>
            <meta property="og:url" content="x"/>
            <meta property="og:image" content="x"/>
            <meta property="og:site_name" content="x"/>
            <meta property="og:description" content="x"/>
        '''
        r = requests.get(params['link'])
        soup = BeautifulSoup(r.text)

        # check to see if the page uses Facebook Metatags and if so save them
        for metatag in soup.findAll('meta'):
            prop = metatag.get('property')
            #if prop == 'og:url':
            #    params['link'] = prop.get('content')
            if prop == 'og:image':
                params['picture'] = metatag.get('content')
            elif prop == 'og:title':
                params['name'] = metatag.get('content')
            elif prop == 'og:descripton':
                params['description'] = metatag.get('content')

        # if the metatags were not set then see if you can generate some
        # default options for your facebook parameters starting with images
        if not 'picture' in params:
            # TODO
            # grab some image that meets a basic width/height requirement
            # and try to filter out anything which shows up in the footer
            # or nav, or anything that looks like it might be an ad banner
            # etc.
            pass
        if not 'name' in params:
            # check to see if the page has a title to use for links name
            if soup.title:
                params['name'] = soup.title.text
        if not 'description' in params:
            # check if there is a regular descritption meta tag we can use
            descrip = soup.find('meta', attrs={'name': 'description'})
            if descrip:
                params['description'] = descrip.get('content')

        return params


    def getManagedPages(self, request, biz_id=None):
        ''' Get all the Facebook pages a user manages, or a
        single page, assuming the optional biz_id arg is given
        '''
        try:
            if biz_id:
                return FacebookManagedPages.objects.get(
                    user_id=self.user_id, biz_id=biz_id, ignored=0)
            else:
                return FacebookManagedPages.objects.filter(
                    user_id=self.user_id, ignored=0)
        except FacebookManagedPages.DoesNotExist:
            return None

    def updateManagedPages(self, request):
        '''Get my managed accounts
        '''
        #r = requests.get(self.make_url("me/accounts",
        #                    {'access_token':self.access_token}))
        r = requests.get(FACEBOOK_GRAPH_URL+"me/accounts",
                params={'access_token':self.access_token})
        fb_data = r.json
        self._handleErrors(fb_data)

        # grab all the pages you are managing on facebook
        # make a generator obj full of dicts containing both the original
        # JSON response and the Django DB obj that response should create
        page_objs = ({
            'obj':FacebookManagedPages(
                    user_id=self.user_id,
                    name=x['name'],
                    category=x['category'],
                    fbook_uid=x['id'],
                    perms=x['perms'],
                    access_token=x['access_token'],
                    ignored=False),
            'json':x
        } for x in fb_data['data'] if x['category'] != 'Application')


        # save new managed pages to the DB, ignore existing pages
        for page in page_objs:
            try:
                rs = FacebookManagedPages.objects.get(
                    user_id=request.user.id,
                    name=page['json']['name'],
                    fbook_uid=page['json']['id'])

                # update the permissions field in case it changed
                rs.perms = page['json']['perms']
                rs.access_token = page['json']['access_token']
                rs.save()

            except FacebookManagedPages.DoesNotExist:
                page['obj'].save()

    def useManagedPage(self, biz_id):
        ''' switch tokens to use your managed page token
        and henceforth access facebook using it instead.
        '''
        account = self.getManagedPages(biz_id=biz_id)
        self.access_token     = account.access_token
        self.facebook_id      = account.fbook_uid
        self.token_expiration = None


    def getPagesMessages(self):
        '''Read all messages for a managed page.
        NOTE: you need the read_mailbox, and
        managed_page permission
        THE GET REQUEST:
        https://graph.facebook.com/PAGE_ID/conversations?access_token=<TOKEN>
        '''
        # https://developers.facebook.com/blog/post/2012/03/14/new-page-apis/
        pass

    def replyToPagesMessage(self):
        ''' Reply to a page message you got from using the
        getPagesMessages() function. you can reply to the message.
        by issuing an HTTP POST request:
        "https://graph.facebook.com/THREAD_ID/messages?access_token=__"

        a thread looks like:
            t_id.21647763845134

        and if the call is successful it will return the id of the new message
            {"id":"m_id.325810694131945"}

        NOTE: requires read_mailbox and manage_page permissions
        '''
        pass

    def editPageAttributes(self):
        ''' Edit a pages attributes and about section
        https://developers.facebook.com/blog/post/2012/03/14/new-page-apis/
        '''
        pass

    def sync_managed_posts(self, biz_id):
        ''' Query facebook to get a list of all upcoming/scheduled posts
        for a managed facebook page. Then update the insightFever database
        https://developers.facebook.com/docs/reference/api/page/#unpub_scheduled_posts
        https://developers.facebook.com/docs/reference/fql/stream
            post_id      - the id of the post
            source_id    - the fbook_uid for the managed page
            created_time - the unix time stamp for when the post is to be pusblished
            message      - the content of the post
        '''
        page = FacebookManagedPages.objects.get(
                    user_id=self.user_id, biz_id=biz_id, ignored=0)
        fql = (
            "SELECT post_id, source_id, created_time, message "
            "FROM stream WHERE source_id={} "
            "AND is_published=0".format(page.fbook_uid)
            )
        url = self.get_FQL(fql, page.access_token)
        r = requests.get(url)
        return r.json
        """
        facebook_posts = r.json
        data = facebook_posts['data']
        for d in data:
            posttime = datetime.fromtimestamp(d['created_time'])

            # check if this post_id is in the DB
            try:
                mypost = PostQueue.objects.get(fbook_post_id=d['post_id'])
            except PostQueue.DoesNotExist:
                # add the post to the insight fever DB
                newpost = PostQueue(
                    created_by=self.user_id,
                    created_on=datetime.datetime.utcnow().replace(tzinfo=utc),
                    biz_id=biz_id,
                    social_sites=[u'facebook'],
                    post_date=posttime,
                    message=d['message'],
                    status='active',
                    fbook_post_id=d['post_id'],
                    )

        """

    #-----------------------------------------------------------------------------
    # ACCESS TOKENS
    #-----------------------------------------------------------------------------

    def getAccessToken(self, request):
        ''' Get an access token
        https://graph.facebook.com/oauth/access_token?
        client_id=YOUR_APP_ID&
        client_secret=YOUR_APP_SECRET&
        grant_type=client_credentials

        NOTE: oauth returns the access token as plain text
              not as JSON
        '''
        user_social = UserSocialAuth.objects.get(
                        user_id=request.user.id, provider="facebook")
        return user_social.extra_data['access_token']

    def refreshAccessToken(self, request):
        ''' refreshes the users short lived access token in the DB
        '''
        params = {
            'client_id'    : settings.FACEBOOK_APP_ID,
            'client_secret': settings.FACEBOOK_API_SECRET,
            'access_token' : self.access_token,
            'redirect_uri' : settings.FACEBOOK_REDIRECT_URI,
            'grant_type'   : 'refresh_token',
            }
        result = requests.get(ACCESS_TOKEN_URL, params=params)
        self._handleErrors(result.json)
        return result.json

    def getLongLivedToken(self, request):
        """ Exchanges the access token for a 60 day token.

        https://graph.facebook.com/oauth/access_token?
        client_id=APP_ID&
        client_secret=APP_SECRET&
        grant_type=fb_exchange_token&
        fb_exchange_token=EXISTING_ACCESS_TOKEN
        """
        params = {
            'client_id' :    settings.FACEBOOK_APP_ID,
            'client_secret': settings.FACEBOOK_API_SECRET,
            'grant_type':    'fb_exchange_token',
            'fb_exchange_token': self.access_token
            }
        result = requests.get(ACCESS_TOKEN_URL, params=params)

        # return dict((k, v[0]) for k, v in result.json)
        if result.json:
            self._handleErrors(request, result.json)
            # save your new long lived token to the DB here

            return result.json
        return result.text


    @classmethod
    def _handleErrors(self, request, rs):
        ''' http://fbdevwiki.com/wiki/Error_codes
        Function that generates different actions and responses
        based on what errors the facebook API returns
        '''
        if 'code' in rs:
            log.error('code, indicates a redirect for oauth authentication')

        if 'error' in rs:
            # TODO - handle multiple errors at once
            """
            # NOTE: there a subcode does not always exist
            code     = rs['error']['code']
            subcode  = rs['error']['error_subcode']
            message  = rs['error']['message']
            err_type = rs['error']['type']

            # you have an invalid OAuth 2.0 Access Token
            # https://developers.facebook.com/docs/authentication/access-token-expiration/
            if code == 190:
                if subcode == 463:
                    # your tokens timestamp has expired, renew session
                    pass
                elif subcode == 467:
                    # access token invalidated by logout or password change
                    pass
                elif subcode == 458:
                    # the user has deauthorized your app. make a log of this
                    pass
            """
            log.error(rs['error'])
            messages.error(request, rs['error'])
            #raise FacebookException("{0}: {1}".format(err_type, message))
            raise FacebookException(rs)



"""
ERROR SUBCODES for ERROR CODE 190

456  The session is malformed.
457  The session has an invalid origin.
458  The session is invalid, because the app is no longer installed.
459  The user has been checkpointed. The error_data will contain the URL the user needs to go to to clear the checkpoint.
460  The session is invalid likely because the user changed the password.
461  The session is invalid, because the user has reinstalled the app.
462  The session has a stale version.
463  The session has expired.
464  The session user is not confirmed.
465  The session user is invalid.
466  The session was explicitly invalidated through an API call.
467  The session is invalid, because the user logged out.
468  The session is invalid, because the user has not used the app for a long time.

"""
#-----------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------

def is_token_expired(request):
    data = UserSocialAuth.objects.get(
        user_id=request.user.id, provider='facebook')

    # this datetime format is surely wrong.
    # TODO - turn this into datetime seconds
    expires_in = datetime.datetime(seconds=data['expires'])

    # TODO
    # get the date of when the token was last updated, and find out
    # if the time has elapsed already. If it has, then refresh the token
    token_last_updated = 'GET LAST UPDATED TIME HERE'
    pass

#-----------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------


def get_facebook_post_data(url):
    ''' Searches a url for Facebook meta tags. If none found
    Then it searches for information it can use to fill the
    following parameters: picture, name, caption, description.
    META TAG EXAMPLES:
        <meta property="og:title" content="x"/>
        <meta property="og:type" content="x"/>
        <meta property="og:url" content="x"/>
        <meta property="og:image" content="x"/>
        <meta property="og:site_name" content="x"/>
        <meta property="og:description" content="x"/>
    '''
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    params = {}

    params['link'] = url

    # check to see if the page uses Facebook Metatags and if so save them
    for metatag in soup.findAll('meta'):
        prop = metatag.get('property')
        #if prop == 'og:url':
        #    params['link'] = prop.get('content')
        if prop == 'og:image':
            params['picture'] = metatag.get('content')
        elif prop == 'og:title':
            params['name'] = metatag.get('content')
        elif prop == 'og:descripton':
            params['description'] = metatag.get('content')

    # if the metatags were not set then see if you can generate some
    # default options for your facebook parameters starting with images
    if not 'picture' in params:
        # TODO
        # grab some image that meets a basic width/height requirement
        # and try to filter out anything which shows up in the footer
        # or nav, or anything that looks like it might be an ad banner
        # etc.
        pass
    if not 'name' in params:
        # check to see if the page has a title to use for links name
        if soup.title:
            params['name'] = soup.title.text
    if not 'description' in params:
        # check if there is a regular descritption meta tag we can use
        descrip = soup.find('meta', attrs={'name': 'description'})
        if descrip:
            params['description'] = descrip.get('content')

    return params



#-----------------------------------------------------------------------------
# URL CONSTRUCTION
#-----------------------------------------------------------------------------


def make_url(path, args=None):
    ''' Generate urls for posting to Facebook
    '''
    if not args: args = {}
    url = 'https://graph.facebook.com/{0}?{1}'.format(
                    path, urllib.urlencode(args))
    return url


def decode_url(url):
    ''' Decodes a url'''
    return urlparse.parse_qs(url)


def remove_query_param(url, key):
    p   = re.compile('%s=[^=&]*&' % key, re.VERBOSE)
    url = p.sub('', url)
    p   = re.compile('%s=[^=&]*' % key, re.VERBOSE)
    url = p.sub('', url)
    return url


def replace_query_param(url, key, value):
    p = re.compile('%s=[^=&]*' % key, re.VERBOSE)
    return p.sub('%s=%s' % (key, value), url)


#-----------------------------------------------------------------------------
# GETTING AND UPDATING TOKENS / PERMISSIONS
#-----------------------------------------------------------------------------


def renew_access_token(user_id):
    ''' refreshes the users short lived access token in the DB
    '''
    info = UserSocialAuth.objects.get(user_id=user_id, provider='facebook')
    facebook_uid = info.extra_data['id']
    params = {
        'client_id':     settings.FACEBOOK_APP_ID,
        'client_secret': settings.FACEBOOK_API_SECRET,
        'access_token':  info.extra_data['access_token']
        }
    url = make_url('WHATEVER', params)



def request_long_lived_token(user_id):
    ''' Request the 60 day long lived access token
    https://developers.facebook.com/roadmap/offline-access-removal/


    https://graph.facebook.com/oauth/access_token?
    client_id=APP_ID&
    client_secret=APP_SECRET&
    grant_type=fb_exchange_token&
    fb_exchange_token=EXISTING_ACCESS_TOKEN

    NOTE - PAGE ACCESS TOKENS
    When a user grants an app the manage_pages permission, the app is
    able to obtain page access tokens for pages that the user administers
    by querying the [User ID]/accounts Graph API endpoint. With the
    migration enabled, when using a short-lived user access token to
    query this endpoint, the page access tokens obtained are short-lived
    as well.

    Exchange the short-lived user access token for a long-lived access token
    using the endpoint and steps explained earlier. By using a long-lived
    user access token, querying the [User ID]/accounts endpoint will now
    provide page access tokens that do not expire for pages that a user
    manages. This will also apply when querying with a non-expiring user
    access token obtained through the deprecated offline_access permission.
    '''
    # query the PostQueue model to get this users existing access token
    # and put it in here
    params = {
        'client_id':         settings.FACEBOOK_APP_ID,
        'client_secret':     settings.FACEBOOK_API_SECRET,
        'grant_type':        'fb_exchange_token',
        'fb_exchange_token': '<EXISTING_ACCESS_TOKEN>',
        }
    url    = make_url('oauth/access_token', params)
    result = requests.get(url)
    return dict((k, v[0]) for k, v in result.json)


#-----------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------

def post_as_page(fbook_id, token, msg):
    ''' Post to facebook wall as page
    fbook_id - the id you want to post as
    token    - the access token for the page you want to post as
    msg      - the message PostQueue object you want to post
    '''
    post_data = {
        'access_token': token,
        'message':      msg.message,
        }
    url    = make_url(str(fbook_id)+'/feed', post_data)
    result = request.get(url)
    return result.json


#-----------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------

# facebook error code handling

def handle_fbook_errors(request, rs):
    ''' http://fbdevwiki.com/wiki/Error_codes
    Function that generates different actions and responses
    based on what errors the facebook API returns
    '''
    if not rs.has_key('error'):
        pass
    else:
        # TODO - handle multiple errors at once
        code     = rs['error']['code']
        subcode  = rs['error']['error_subcode']
        message  = rs['error']['message']
        err_type = rs['error']['type']

        # log the error and print message to screen
        print(rs['error'])
        log.error(rs['error'])
        messages.error(request, "{}: {}".format(err_type, message))

        if code == 190:
            # you have an invalid OAuth 2.0 Access Token

            if subcode == 463:
                # your tokens timestamp has expired and you must renew your session

                # TODO - fix this so that you can programatically log back in to facebook
                request.method = 'POST'
                return render(request, 'reports/social/facebook.html', {})
                #return redirect('social_auth.socialauth_begin', kwargs={'backend':'facebook'})
                #auth(request, 'facebook')



def auth_process(request, backend):
    """Authenticate using social backend
    """
    # Save any defined next value into session
    data = request.POST if request.method == 'POST' else request.GET

    if REDIRECT_FIELD_NAME in data:
        # Check and sanitize a user-defined GET/POST next field value
        redirect = data[REDIRECT_FIELD_NAME]
        if setting('SOCIAL_AUTH_SANITIZE_REDIRECTS', True):
            redirect = sanitize_redirect(request.get_host(), redirect)
        request.session[REDIRECT_FIELD_NAME] = redirect or DEFAULT_REDIRECT

    # Clean any partial pipeline info before starting the process
    clean_partial_pipeline(request)

    if backend.uses_redirect:
        return HttpResponseRedirect(backend.auth_url())
    else:
        return HttpResponse(backend.auth_html(),
                            content_type='text/html;charset=UTF-8')



