from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group
from django.conf import settings
from guardian.shortcuts import *

from myproject.apps.biz.models import Business, Website, WebsiteTypes

import re
import string

from django.utils.safestring import SafeData, mark_safe
from django.utils.encoding import force_unicode
from django.utils.functional import allow_lazy

#-----------------------------------------------------------------------------
# FEVER UTILITIES
#-----------------------------------------------------------------------------
# A collections of functions that perform common tasks specific to insightFever

def getBiz(biz):
    ''' Return useful information about a Business
    Accepts either a biz_id or a biz_name
    '''
    if biz:
        if isinstance(biz, basestring):
            # return the biz_id using the name
            try:
                return Business.objects.get(biz_name=biz)
            except Business.DoesNotExist:
                return None
        elif isinstance(biz, int):
            # return biz name and other details
            try:
                return Business.objects.get(biz_id=biz)
            except Business.DoesNotExist:
                return None
        else:
            raise Business.DoesNotExist


#-----------------------------------------------------------------------------
# FEVER PERMISSIONS
#-----------------------------------------------------------------------------
# Functions related to permissions, groups, and users

# assign,
# get_perms, remove_perm, get_perms_for_model, get_users_with_perms,
# get_groups_with_perms, get_objects_for_user, get_objects_for_group

def can_view_perms(self, user, perms=None):
    ''' Check via Guardian if user has permissions to view the object

    if not profile.can_view_profile(request.user):
        return HttpResponseForbidden(_("You don't have permission to view this profile."))

    TODO:
    primary user gets created
    primary user gets assigned Client_Superuser group
    primary user creates new business
    primary user creates websites for their new business

    primary user creates new underlings
    if underlings.count() > 0:
        then add-websites page includes a dropdown
        form for setting access to that website

    primary user can create 5-10 custom groups.
    default groups are: full_access, limited_access, read_only (or something similar)
    when primary user creates new user, they can assign group to them.

    When a models save method is triggered use Django Signals to
    assign necessary permissions or check them if needs be.
    '''
    # get all users who have all the matching permssions
    matching_users = get_users_with_perms(self)

    if user in matching_users:
        return True

    # Registered users.
    elif self.privacy == 'limited_access' and isinstance(user, User):
        return True

    # Checks done by guardian for owner and admins.
    elif 'view_yelp' in get_perms(user, self):
        return True

    return False


def get_user_businesses(user):
    '''Return list of all businesses the user has permission to administer
    '''
    if isinstance(user, int):
        user_id = user
    else:
        user_id = user.id
    return Business.objects.filter(members__exact=user_id)


def can_manage_biz(biz, user):
    '''Checks to see if the user has permission to manage the
    businesses
    '''
    # TODO - do this via Django Guardian
    pass


#-----------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------

def find_url(text):
    ''' finds and extracts a list of urls from within the text
    if none are found it returns None
    Regular expressions taken from:
    https://github.com/dryan/twitter-text-py/blob/master/twitter_text/regex.py
    '''
    punct = re.escape(string.punctuation)
    REGEXEN = {}
    REGEXEN['valid_preceding_chars'] = re.compile(ur"(?:[^\/\"':!=]|^|\:)")
    REGEXEN['valid_domain'] = re.compile(ur'(?:[^%s\s][\.-](?=[^%s\s])|[^%s\s]){1,}\.[a-z]{2,}(?::[0-9]+)?' % (punct, punct, punct), re.IGNORECASE)
    REGEXEN['valid_url_path_chars'] = re.compile(ur'[\.\,]?[a-z0-9!\*\'\(\);:=\+\$\/%#\[\]\-_,~@\.]', re.IGNORECASE)
    REGEXEN['valid_url_path_ending_chars'] = re.compile(ur'[a-z0-9\)=#\/]', re.IGNORECASE)
    REGEXEN['valid_url_query_chars'] = re.compile(ur'[a-z0-9!\*\'\(\);:&=\+\$\/%#\[\]\-_\.,~]', re.IGNORECASE)
    REGEXEN['valid_url_query_ending_chars'] = re.compile(ur'[a-z0-9_&=#]', re.IGNORECASE)
    REGEXEN['valid_url'] = re.compile(r'''
    (%s)
    (
        (https?:\/\/|www\.)
        (%s)
        (/%s*%s?)?
        (\?%s*%s)?
    )
    ''' % (
        REGEXEN['valid_preceding_chars'].pattern,
        REGEXEN['valid_domain'].pattern,
        REGEXEN['valid_url_path_chars'].pattern,
        REGEXEN['valid_url_path_ending_chars'].pattern,
        REGEXEN['valid_url_query_chars'].pattern,
        REGEXEN['valid_url_query_ending_chars'].pattern
    ),
    re.IGNORECASE + re.X)
    # groups:
    # 1 - Preceding character
    # 2 - URL
    # 3 - Protocol or www.
    # 4 - Domain and optional port number
    # 5 - URL path
    # 6 - Query string
    foo = re.search(REGEXEN['valid_url'], text)
    return foo

#-----------------------------------------------------------------------------
# 
#-----------------------------------------------------------------------------
# Configuration for urlize() function.
TRAILING_PUNCTUATION = ['.', ',', ':', ';']
WRAPPING_PUNCTUATION = [('(', ')'), ('<', '>'), ('&lt;', '&gt;')]

# List of possible strings used for bullets in bulleted lists.
DOTS = [u'&middot;', u'*', u'\u2022', u'&#149;', u'&bull;', u'&#8226;']

unencoded_ampersands_re = re.compile(r'&(?!(\w+|#\d+);)')
unquoted_percents_re = re.compile(r'%(?![0-9A-Fa-f]{2})')
word_split_re = re.compile(r'(\s+)')
simple_url_re = re.compile(r'^https?://\w')
simple_url_2_re = re.compile(r'^www\.|^(?!http)\w[^@]+\.(com|edu|gov|int|mil|net|org)$')
simple_email_re = re.compile(r'^\S+@\S+\.\S+$')
link_target_attribute_re = re.compile(r'(<a [^>]*?)target=[^\s>]+')
html_gunk_re = re.compile(r'(?:<br clear="all">|<i><\/i>|<b><\/b>|<em><\/em>|<strong><\/strong>|<\/?smallcaps>|<\/?uppercase>)', re.IGNORECASE)
hard_coded_bullets_re = re.compile(r'((?:<p>(?:%s).*?[a-zA-Z].*?</p>\s*)+)' % '|'.join([re.escape(x) for x in DOTS]), re.DOTALL)
trailing_empty_content_re = re.compile(r'(?:<p>(?:&nbsp;|\s|<br \/>)*?</p>\s*)+\Z')
del x # Temporary variable


def find_urls(text, trim_url_limit=None):
    """
    Converts any URLs in text into clickable links.

    Works on http://, https://, www. links, and also on links ending in one of
    the original seven gTLDs (.com, .edu, .gov, .int, .mil, .net, and .org).
    Links can have trailing punctuation (periods, commas, close-parens) and
    leading punctuation (opening parens) and it'll still do the right thing.

    If trim_url_limit is not None, the URLs in link text longer than this limit
    will truncated to trim_url_limit-3 characters and appended with an elipsis.

    If nofollow is True, the URLs in link text will get a rel="nofollow"
    attribute.

    If autoescape is True, the link text and URLs will get autoescaped.

    EXAMPLE:
        msg = "hello how are http://www.google.com txt www.reddit.com and also cnn.com end"
        foo = find_urls(msg)
    """
    trim_url = lambda x, limit=trim_url_limit: limit is not None and (len(x) > limit and ('%s...' % x[:max(0, limit - 3)])) or x
    safe_input = isinstance(text, SafeData)
    words = word_split_re.split(force_unicode(text))
    output = []
    for i, word in enumerate(words):
        match = None
        if '.' in word or '@' in word or ':' in word:
            # Deal with punctuation.
            lead, middle, trail = '', word, ''
            for punctuation in TRAILING_PUNCTUATION:
                if middle.endswith(punctuation):
                    middle = middle[:-len(punctuation)]
                    trail = punctuation + trail
            for opening, closing in WRAPPING_PUNCTUATION:
                if middle.startswith(opening):
                    middle = middle[len(opening):]
                    lead = lead + opening
                # Keep parentheses at the end only if they're balanced.
                if (middle.endswith(closing)
                    and middle.count(closing) == middle.count(opening) + 1):
                    middle = middle[:-len(closing)]
                    trail = closing + trail

            # Make URL we want to point to.
            url = None
            if simple_url_re.match(middle):
                url = middle
            elif simple_url_2_re.match(middle):
                url = "http://%s" % middle
            elif not ':' in middle and simple_email_re.match(middle):
                local, domain = middle.rsplit('@', 1)
                try:
                    domain = domain.encode('idna')
                except UnicodeError:
                    continue
                url = 'mailto:%s@%s' % (local, domain)

            # Make link.
            if url:
                trimmed = trim_url(middle)
                output.append(mark_safe('%s%s%s' % (lead, middle, trail)))
    return output



