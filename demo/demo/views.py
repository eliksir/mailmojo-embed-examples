import json
import requests
from base64 import b64encode
from datetime import datetime, timedelta
from django.conf import settings
from django.shortcuts import Http404, redirect, render


AUTH_KEY = b64encode('{0}:{1}'.format(settings.CLIENT_ID, settings.CLIENT_SECRET))


def get_access_token():
    """Retrieve top level access-token."""
    data = {
        'grant_type': 'client_credentials',
    }
    headers = {
        'Authorization': 'Basic {}'.format(AUTH_KEY)
    }
    r = requests.post(settings.API_TOKEN_URL, data=data, headers=headers)
    return json.loads(r.text)


def get_grant_code(username, token):
    """Retrieve grant code for user."""
    data = {'username': username}
    headers = {'Authorization': 'Bearer {}'.format(token)}
    r = requests.post(settings.API_GRANT_URL, data=data, headers=headers)
    user_grant_info = json.loads(r.text)
    return user_grant_info.get('grant_code')


def get_user_access_token(grant_code):
    """Retrieve access-token for user."""
    data = {
        'grant_type': 'authorization_code',
        'code': grant_code
    }
    headers = {'Authorization': 'Basic {}'.format(AUTH_KEY)}
    r = requests.post(settings.API_TOKEN_URL, data=data, headers=headers)
    return json.loads(r.text)


def get_embed_url(user_access_token, ip, custom_css=None):
    data = {
        'session_type': 'newsletter',
        'user_ip': ip,
        'options': {
            'skip_recipients_step': True,
            'lang': 'no',
        }
    }
    if custom_css == 'yes':
        data['options']['css'] = settings.CSS_URL

    print data

    headers = {
      'Authorization': 'Bearer {}'.format(user_access_token),
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
    req = requests.post('{}/embed'.format(settings.API_BASE_URL),
                        data=json.dumps(data),
                        headers=headers)
    return req.headers.get('Location')


def home(request):
    """Handles creating access token for given user."""
    if 'force_update' in request.GET:
        del request.session['access_token']
        del request.session['access_token_expires_at']
        if 'user_access_token' in request.session:
            del request.session['user_access_token']

    # Make sure we have a valid top level access-token
    if ('access_token' not in request.session or
            request.session['access_token_expires_at'] < datetime.now().strftime('%s')):
        token_info = get_access_token()
        if 'access_token' not in token_info:
            raise Http404

        request.session['access_token'] = token_info['access_token']
        request.session['access_token_expires_at'] = (datetime.now() +
                timedelta(seconds=token_info['expires_in'])).strftime('%s')

    # Creates new user_access_token for specified username
    if request.POST.get('username'):
        grant_code = get_grant_code(username=request.POST['username'],
                                    token=request.session['access_token'])
        if grant_code:
            token_info = get_user_access_token(grant_code)
            request.session['user_access_token'] = token_info['access_token']
            # Support custom CSS or not
            request.session['custom_css'] = request.POST.get('custom_css')
            return redirect('newsletter')

    return render(request, 'home.html')


def newsletter(request):
    """Open iframe with embed newsletter for given user."""
    user_access_token = request.session.get('user_access_token')
    if not user_access_token:
        return redirect('home')

    embed_url = get_embed_url(user_access_token,
                              ip=request.META['REMOTE_ADDR'],
                              custom_css=request.session.get('custom_css'))
    return render(request, 'newsletter.html', {
        'embed_url': embed_url
    })
