import json
import requests
from base64 import b64encode
from datetime import datetime, timedelta
from django.conf import settings
from django.shortcuts import Http404, redirect, render

from .forms import EmbedForm


AUTH_KEY = b64encode('{0}:{1}'.format(settings.CLIENT_ID, settings.CLIENT_SECRET))


def get_access_token():
    """Retrieve top level access-token."""
    data = {
        'grant_type': 'client_credentials'
    }
    headers = {
        'Authorization': 'Basic {}'.format(AUTH_KEY)
    }
    r = requests.post(settings.API_TOKEN_URL, data=data, headers=headers)
    #print "[Super Access Token] ", r.text
    return json.loads(r.text)


def get_user_access_token(username, token):
    """Retrieve access-token for user."""
    data = {
        'grant_type': 'password',
        'username': username,
        'password': token,
    }
    headers = {'Authorization': 'Basic {}'.format(AUTH_KEY)}
    r = requests.post(settings.API_TOKEN_URL, data=data, headers=headers)
    #print "[User Access Token] ", r.text
    return json.loads(r.text)


def get_embed_url(user_access_token, ip, options=None):
    data = {
        'session_type': 'newsletter',
        'user_ip': ip,
        'options': {'lang': 'nb'}
    }

    data['options']['lang'] = options.get('lang')
    data['options']['css'] = settings.CSS_URL if options.get('css') else None
    data['options']['skip_recipients_step'] = options.get('skip_recipients_step')

    headers = {
      'Authorization': 'Bearer {}'.format(user_access_token),
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
    req = requests.post('{}/embed'.format(settings.API_BASE_URL),
                        data=json.dumps(data),
                        headers=headers)
    return req.headers.get('Location')


def _validate_or_set_super_token(request):
    """Make sure we have a valid top level access-token."""
    if ('access_token' not in request.session or
            request.session['access_token_expires_at'] < datetime.now().strftime('%s')):
        token_info = get_access_token()
        if not token_info.get('access_token'):
            raise Http404

        request.session['access_token'] = token_info['access_token']
        request.session['access_token_expires_at'] = (datetime.now() +
                timedelta(seconds=token_info['expires_in'])).strftime('%s')


def _validate_or_set_user_token(request, username):
    """Retrieve access token if we do not have any or has expired."""
    if ('user_access_token' not in request.session or
            request.session['uat_expires_at'] < datetime.now().strftime('%s')):

        # Creates new user_access_token for specified username
        token_info = get_user_access_token(username, token=request.session['access_token'])
        if not token_info.get('access_token'):
            raise Http404

        request.session['user_access_token'] = token_info['access_token']
        request.session['uat_expires_at'] = (datetime.now() +
                timedelta(seconds=token_info['expires_in'])).strftime('%s')


def home(request):
    """Handles creating super token and token for given user."""
    _validate_or_set_super_token(request)

    if request.POST:
        form = EmbedForm(request.POST)

        if form.is_valid():
            _validate_or_set_user_token(request, form.cleaned_data['username'])

            # Options
            request.session['options'] = {
                'lang': form.cleaned_data['lang'],
                'css': form.cleaned_data['css'],
                'skip_recipients_step': form.cleaned_data['skip_recipients_step'],
            }
            return redirect('newsletter')
    else:
        form = EmbedForm()
    return render(request, 'home.html', {'form': form})


def force_update(request):
    """Removes all access tokens in session."""
    keys = ('access_token', 'access_token_expires_at', 'user_access_token',
            'uat_expires_at')
    for session_key in keys:
        if session_key in request.session:
            del request.session[session_key]
    return redirect('home')


def newsletter(request):
    """Open iframe with embed newsletter for given user."""
    user_access_token = request.session.get('user_access_token')
    if not user_access_token:
        return redirect('home')

    embed_url = get_embed_url(user_access_token,
                              ip=request.META['REMOTE_ADDR'],
                              options=request.session.get('options'))
    return render(request, 'newsletter.html', {
        'embed_url': embed_url
    })
