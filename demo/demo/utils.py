import json
import requests
from base64 import b64encode
from django.conf import settings


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
