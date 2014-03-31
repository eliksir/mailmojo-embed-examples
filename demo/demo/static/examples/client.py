# Simple example usage of MailMojo's API for creating embedded newsletter
# sessions, here implemented in Python 2 using only standard libraries.
#
# The API uses OAuth2 for authorization. This example will not go into details
# of how OAuth2 works, but will show low level requests so you get an idea of
# exactly how they work. In your own code you'll most likely be able to use an
# OAuth2 library to simplify your implementation. In Python for example this
# could be oauthlib.
#
# For more details on OAuth2 itself, see RFC 6749 at
# http://tools.ietf.org/html/rfc6749
#
# We have implemented one extension of the OAuth2 spec, which is an extra
# endpoint to get grant codes (used to get access tokens) for users associated
# with the currently authorized user (i.e. customers of Webtop). This endpoint
# returns a grant code directly for easier API requests without the redirect
# workflow as specified in the OAuth2 authorization code grant type.


# For this example we need to be able to make HTTP requests, encode credentials
# as base64 and encode/decode JSON data. These are all standard Python
# libraries for this exact functionality.
import json
from base64 import b64encode
from urllib import urlencode
from urllib2 import Request, urlopen


# The token and grant URLs are the only API endpoints you can assume exists.
# For other API endpoints the URLs may and WILL change, so you are required to
# navigate the API and get URLs to resources you need by reading HATEOAS
# responses. The URLs may however be cached by your client to avoid discovering
# the endpoints through the API at all times. If so, fallback code to handle
# cases when the URLs change must be in place. We'll show an example of URL
# discovery in step 2 below.
API_BASE_URL = 'https://api.mailmojo.no'
API_TOKEN_URL = '{}/oauth/token'.format(API_BASE_URL)
API_GRANT_URL = '{}/oauth/grant_code'.format(API_BASE_URL)

# You will be provided with a client identifier (UUID) and secret. These MUST
# be stored securely and never exposed to any user agent (i.e. HTML/JS). Your
# client ID and secret can be retrieved by logging into your MailMojo account
# at https://v2.mailmojo.no and navigating to "API-tilgang" within "Min konto".
# Webtop has an account with the username "webtopsolutions".
CLIENT_ID = '87ce8b97-6e6a-4ac4-8aaa-b8c53fcf365a'
CLIENT_SECRET = 'a secret, secure, unguessable passcode'
# Base 64 encode client credentials for HTTP Basic Auth
CLIENT_AUTH_KEY = b64encode('{0}:{1}'.format(CLIENT_ID, CLIENT_SECRET))


# ------
# Step 1: Get top level access token for the Webtop system
#
# OAuth2 uses access tokens for API calls, so first we need to get one. Webtop
# as an integration partner is allowed to use the client credentials
# authorization grant type (defined in the OAuth2 spec). This makes it easy to
# get an access token for your top level MailMojo account.

# Set up a POST request against the token endpoint with parameters as
# x-www-form-urlencoded in the body and header for HTTP Basic Auth.
request = Request(API_TOKEN_URL,
                  data=urlencode({
                      'grant_type': 'client_credentials',
                      # TODO: Supported scopes will be provided soon
                      #'scope': '...'
                  }),
                  headers={
                      'Authorization': 'Basic {}'.format(CLIENT_AUTH_KEY)
                  })
response = urlopen(request)

# The response body is JSON encoded data containing an object similar to this:
#   {
#     'access_token': 'izf1wvfRA5iZWmNdzXBu80zLgZPPTb',
#     'expires_in': 2592000,
#     'token_type': 'Bearer',
#     'scope': '...'
#   }
token_info = json.loads(response.read())

# Store the access token i.e. in your database for future API calls, but the
# token WILL expire after a period of time (currently 1 month). At that point
# (identified by 403 Forbidden or 401 Not Authorized responses to API calls
# made with your top level access token), you'll have to perform a new
# request to retrieve a new access token.
access_token = token_info['access_token']


# ------
# Step 2: Get current top level API endpoints available
#
# Now we're ready to make our first actual call to an API endpoint, this will
# show basically how all API calls will be made. Though usually you'll be doing
# API calls with a user access token, as we'll show how to get later.

# For regular API calls we use the access token, identified by its Bearer type,
# in the HTTP Authorization header.

# TODO: Show simple GET API request to root
# COMING SOON -- FOR THE TIME BEING NOT NEEDED


# ------
# Step 3: Get grant code for a user
#
# To get a regular access token for a user, you'll first need to get a grant
# code for the specific user. This is because you don't have any regular
# credentials to ask for an access token for the user with. Instead you ask on
# behalf of your top level access token to get a grant code for the user.
#
# You will need to supply the MailMojo username of the user you want to get a
# grant code for. (This will probably follow some convention of mapping from
# Webtop -> MailMojo.)
#
# This endpoint will return a 401/403 response if the access token used to
# access it is invalid/has expired.

# Set up a POST request against the grant code endpoint, again with parameters
# sent as x-www-form-urlencoded in the body, with the top level access token.
request = Request(API_GRANT_URL,
                  data=urlencode({
                      'username': 'exampleuser'
                  }),
                  headers={
                      'Authorization': 'Bearer {}'.format(access_token)
                  })
response = urlopen(request)

# The response body for this simply contains a grant code encoded as JSON, and
# looks similar to this:
#   {
#     'grant_code': 'Awvn1cRrnr82Fyva0yoJ8T1tpP05KB'
#   }
user_grant_info = json.loads(response.read())

# Store the grant code temporarily for the next step. There is no need to
# store this permanently as it will expire immediately upon use (additionally
# it will auto-expire after a couple of minutes if not yet used).
grant_code = user_grant_info['grant_code']


# ------
# Step 4: Get a user access token
#
# The user access token is what will allow you to make API calls as a regular
# MailMojo user, i.e. a customer of Webtop with a MailMojo account set up by
# us. This access token will also expire, but you'll also get a refresh token
# which will simplify renewing the access token as shown in step 7.

# Set up a POST request to the token endpoint to get a user access token. This
# is very similar to how you got the top level access token, but this time we
# use code authorization.
request = Request(API_TOKEN_URL,
                  data=urlencode({
                      'grant_type': 'authorization_code',
                      # TODO: Supported scopes will be provided soon
                      #'scope': '...',
                      'code': grant_code
                  }),
                  headers={
                      'Authorization': 'Basic {}'.format(CLIENT_AUTH_KEY)
                  })
response = urlopen(request)

# The response body, again JSON encoded, will be very similar to the response
# for top level access token, but in this case it also contains a refresh
# token, like this:
#   {
#     'access_token': 's7IpoJNMhkJx5Z80PNQZ9o00hVKFL8',
#     'scope': '...',
#     'token_type': 'Bearer',
#     'expires_in': 604800,
#     'refresh_token': 'OE6PNcgmw3AC4lN3MD9Ghq6rh6UFWj'
#   }
token_info = json.loads(response.read())

# Permanently store both the access token for the following API requests, and
# the refresh token for being able to get a new access token once this one
# expires.
user_access_token = token_info['access_token']
user_refresh_token = token_info['refresh_token']


# ------
# Step 5: Create a newsletter embed session
#
# Now that we have an access token for the user, we can make API calls on its
# behalf. We will ask for a new embed session that will give us a unique and
# short lived URL to start a newsletter session. This URL can then be loaded
# in an iframe, presenting the user with the newsletter creation interface.


# Set up a POST request to the embed endpoint as discovered in step 2.
# NOTE: For development/setup/testing, you may hardcode the endpoint as in the
# example below. We will provide info about endpoint discovery ASAP.
#
# For API endpoints apart from OAuth2 specific ones, the parameters must be
# sent as JSON encoded data in the POST body, and you need to provide a
# Content-Type header indicating this.
parameters = {
    # Specify type of embed session, 'newsletter' is currently the
    # only supported type.
    'session_type': 'newsletter',

    # Access to the session will be IP restricted, so here you
    # you need to provide the **end user's** IP address so they'll
    # be able to access the embedded session from their user agent.
    'user_ip': '127.0.0.1',

    # You must also provide some options...
    'options': {

        # Indicates if the embed should skip a step for choosing
        # recipients. 'true' is currently REQUIRED and the only
        # supported value, since the newsletter embed does not
        # yet support choosing recipients manually. Currently we
        # auto-select the main email list from the users's MailMojo
        # account, which will be set up correctly for Webtop customers.
        # REQUIRED option.
        'skip_recipients_step': True,

        # Sets the language of the embedded newsletter process.
        # 'no' and 'en' are supported. Swedish to come. :-)
        # REQUIRED option.
        'lang': 'no',

        # Specify an URL to a CSS file which will be injected into
        # the embedded iframe as a <link> to the CSS file. This
        # allows you to theme the embedded process for better
        # integration into Webtop. Using HTTPS is recommended to
        # avoid the user getting "unsecure content" warnings from
        # the browser (since the iframe itself is served over HTTPS).
        # OPTIONAL: Skip it to get the default theme.
        'css': 'https://example.org/example.css'
    }
}
# NOTE: Currently hardcoded endpoint to https://api.mailmojo.no/embed
request = Request('{}/embed'.format(API_BASE_URL),
                  data=json.dumps(parameters),
                  headers={
                      'Authorization': 'Bearer {}'.format(user_access_token),
                      'Content-Type': 'application/json',
                      'Accept': 'application/json'
                  })
response = urlopen(request)

# The response from the embed endpoint will be 201 Created when successful,
# with no content. The Location header gives the URL of the new embed session.
# If a 401/403 response is returned, the access token has likely expired (the
# content will give further details). See step 7 below for an example of
# getting a new access token for the user.
embed_url = response.info().get('Location')


# ------
# Step 6: Load the embed URL in the end user's browser, typically through an
# iframe. This must be done within a few minutes of creating the embed session,
# as the URL will expire.
#
# Example:
#   <iframe src="<embed_url>" width="800" height="800"></iframe>


# VOILA! At this point the user can successfully create and send a newsletter.
# If however opening the embed URL gives a 403 Forbidden response, the remote
# IP doesn't match the IP supplied during the embed creation process in step 5.
# If it gives 404 Not Found, the embed URL has already been used or has expired
# (it is only valid for a couple of minutes).


# ------
# Step 7: Refresh the user access token
#
# After a while the user access token you got through step 4 will expire.
# When you try to make a new request with this token (to the embed endpoint,
# for instance) you'll get 401/403 responses. When this happens you should
# make a new API call to get an access token, supplying the refresh token you
# got in step 4. This is again very similar to how you've received access
# tokens previously, though this time you use the refresh_token grant type.
request = Request(API_TOKEN_URL,
                  data=urlencode({
                      'grant_type': 'refresh_token',
                      # TODO: Supported scopes will be provided soon
                      #'scope': '...',
                      'refresh_token': user_refresh_token
                  }),
                  headers={
                      'Authorization': 'Basic {}'.format(CLIENT_AUTH_KEY)
                  })
response = urlopen(request)
token_info = json.loads(response.read())

# Done! Now you have a new access token that can be used for step 5 to initiate
# a new embed session. Remember to update your storage of both access token and
# the new refresh token for the user.
new_user_access_token = token_info['access_token']
new_refresh_access_token = token_info['refresh_token']
