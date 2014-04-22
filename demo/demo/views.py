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


def home(request):
    """Handles creating access token for given user."""
    # Make sure we have a valid top level access-token
    if ('access_token' not in request.session or
            request.session['access_token_expires_at'] < datetime.now().strftime('%s')):
        token_info = get_access_token()
        if token_info.get('acces_token'):
            raise Http404

        request.session['access_token'] = token_info['access_token']
        request.session['access_token_expires_at'] = (datetime.now() +
                timedelta(seconds=token_info['expires_in'])).strftime('%s')

    if request.POST:
        form = EmbedForm(request.POST)

        if form.is_valid():
            # Retrieve access token if we do not have any or has expired
            if ('user_access_token' not in request.session or
                    request.session['uat_expires_at'] < datetime.now().strftime('%s')):

                # Creates new user_access_token for specified username
                grant_code = get_grant_code(username=form.cleaned_data['username'],
                                            token=request.session['access_token'])
                if grant_code:
                    token_info = get_user_access_token(grant_code)
                    request.session['user_access_token'] = token_info['access_token']
                    request.session['uat_expires_at'] = (datetime.now() +
                            timedelta(seconds=token_info['expires_in'])).strftime('%s')

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
