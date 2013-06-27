from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from social_auth.models import UserSocialAuth

import tweepy

from myproject.apps.biz.models import Business
#from myproject.apps.social.models import Twitter, Tweets, Followers

#-----------------------------------------------------------------------------
# 
#-----------------------------------------------------------------------------
# Twitter documentation at: https://dev.twitter.com/docs

"""
TODO:

    Make sure you minimize the number of GET request to Twitter as much as possible.
    Your going to want to store all relevant information into your own database
    for each property, and only query for recent info when needed.
"""


def connect_to_tweepy(user_id, biz_id):
    ''' connect to the Twitter API using tweepy
    return an object with all the juicy twitter information
    
    TODO - use session or some other technique to make sure this only
           gets run the first time the user logs in or accesses the
           reports/overview or reports/twitter page.
    '''
    auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, 
                               settings.TWITTER_CONSUMER_SECRET)
    # get current users/biz access token and secret
    try:
        account = UserSocialAuth.objects.get(user_id=user_id, provider="twitter")
    except userSocialAuth.DoesNotExist:
        return None
    tokens = account.extra_data["access_token"].split('&')
    
    # extract the oauth token and oauth token secret from the DB
    # NOTE - we use a for loop b/c order of the fields are not guaranteed.
    for token in tokens:
        if 'oauth_token_secret' in token:
            OAUTH_TOKEN_SECRET = token.split('=')[1]
        else:
            OAUTH_TOKEN = token.split('=')[1]
    
    # set the tokens and return an object ready for accessing Twitter
    auth.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    return tweepy.API(auth)


"""

api = tweepy.API(auth)

# how to update your status
api.update_status('Updating using basic authentication via Tweepy!')

# get the users profile
user_info = api.me()

#-----------------------------------------------------------------------------
# list of commands
#-----------------------------------------------------------------------------

['__class__',
 '__delattr__',
 '__dict__',
 '__doc__',
 '__format__',
 '__getattribute__',
 '__hash__',
 '__init__',
 '__module__',
 '__new__',
 '__reduce__',
 '__reduce_ex__',
 '__repr__',
 '__setattr__',
 '__sizeof__',
 '__str__',
 '__subclasshook__',
 '__weakref__',
 '_lookup_users',
 '_pack_image',
 'add_list_member',
 'api_root',
 'auth',
 'blocks',
 'blocks_ids',
 'cache',
 'create_block',
 'create_favorite',
 'create_friendship',
 'create_list',
 'create_saved_search',
 'destroy_block',
 'destroy_direct_message',
 'destroy_favorite',
 'destroy_friendship',
 'destroy_list',
 'destroy_saved_search',
 'destroy_status',
 'direct_messages',
 'disable_notifications',
 'enable_notifications',
 'exists_block',
 'exists_friendship',
 'favorites',
 'followers',
 'followers_ids',
 'friends',
 'friends_ids',
 'friends_timeline',
 'friendships_incoming',
 'friendships_outgoing',
 'geo_id',
 'geo_search',
 'get_direct_message',
 'get_list',
 'get_saved_search',
 'get_status',
 'get_user',
 'home_timeline',
 'host',
 'is_list_member',
 'is_subscribed_list',
 'list_members',
 'list_subscribers',
 'list_timeline',
 'lists',
 'lists_memberships',
 'lists_subscriptions',
 'lookup_users',
 'me',
 'mentions',
 'nearby_places',
 'parser',
 'public_timeline',
 'rate_limit_status',
 'related_results',
 'remove_list_member',
 'report_spam',
 'retry_count',
 'retry_delay',
 'retry_errors',
 'retweet',
 'retweeted_by',
 'retweeted_by_ids',
 'retweeted_by_me',
 'retweeted_to_me',
 'retweets',
 'retweets_of_me',
 'reverse_geocode',
 'saved_searches',
 'search',
 'search_host',
 'search_root',
 'search_users',
 'secure',
 'send_direct_message',
 'sent_direct_messages',
 'set_delivery_device',
 'show_friendship',
 'subscribe_list',
 'test',
 'trends',
 'trends_available',
 'trends_current',
 'trends_daily',
 'trends_location',
 'trends_weekly',
 'unsubscribe_list',
 'update_list',
 'update_profile',
 'update_profile_background_image',
 'update_profile_colors',
 'update_profile_image',
 'update_status',
 'user_timeline',
 'verify_credentials']

"""

