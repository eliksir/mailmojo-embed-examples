from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.contrib import messages as msg
from django.shortcuts import Http404

from . import utils


class TokenMixin(object):
    def set_token_in_session(self, name, token_info):
        session = self.request.session
        session[name] = token_info['access_token']
        session['{}_expires_at'.format(name)] = (datetime.now() +
                timedelta(seconds=token_info['expires_in'])).strftime('%s')

    def set_user_token(self, token_info):
        if not token_info.get('access_token'):
            msg.error(self.request, "Error: {}".format(token_info.get('error')))
            return False

        self.set_token_in_session('user_access_token', token_info)

    def validate_or_set_super_token(self):
        """Set top level access token in session."""
        session = self.request.session
        if ('access_token' not in session or
                session['access_token_expires_at'] < datetime.now().strftime('%s')):
            token_info = utils.get_access_token()
            if not token_info.get('access_token'):
                raise Http404

            self.set_token_in_session('access_token', token_info)

    def validate_or_set_user_token(self, username):
        """Set user access token in session."""
        session = self.request.session
        if ('user_access_token' not in session or
                session['user_access_token_expires_at'] < datetime.now().strftime('%s')):
            token_info = utils.get_user_access_token(username, token=session['access_token'])
            self.set_user_token(token_info)


class NamedSuccessUrlMixin(object):
    def get_success_url(self):
        url = reverse(self.success_url)
        return url
