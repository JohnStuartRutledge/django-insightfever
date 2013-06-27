"""Example for signing a search request using the oauth2 library."""

import oauth2

# Fill in these values
# YWSID = 'jonNs5sORuMqc1nBG2EJDQ'
consumer_key    = '1goEzbEAojjRUUR6PbQwDQ'
consumer_secret = '9aYd19JVoChuLyTs94b8pCe9TWk'
token           = 'MgXnXTt3LacldmcCQxL9s-jauRj0MLME'
token_secret    = 'MtKlHUrEymAyGcQ-wYtFUgRNnLA'

consumer = oauth2.Consumer(consumer_key, consumer_secret)
url      = 'http://api.yelp.com/v2/search?term=bars&location=sf'

print 'URL: %s' % (url,)

oauth_request = oauth2.Request('GET', url, {})
oauth_request.update({
    'oauth_nonce'       : oauth2.generate_nonce(),
    'oauth_timestamp'   : oauth2.generate_timestamp(),
    'oauth_token'       : token,
    'oauth_consumer_key': consumer_key
    })


token = oauth2.Token(token, token_secret)
oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
signed_url = oauth_request.to_url()
print 'Signed URL: %s' % (signed_url,)

