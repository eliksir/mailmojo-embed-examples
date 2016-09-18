from datetime import datetime, timedelta

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages as msg
from django.shortcuts import Http404

from mm import Auth


class TokenMixin(object):
    def set_token_in_session(self, name, token_info):
        if not token_info.get('access_token'):
            msg.error(self.request, "Error: {}".format(
                token_info.get('error')))
            return False

        session = self.request.session
        session[name] = token_info['access_token']
        session['{}_expires_at'.format(name)] = (
            datetime.now() +
            timedelta(seconds=token_info['expires_in'])
        ).strftime('%s')

    def is_invalid_token(self, name):
        session = self.request.session
        return (
            name not in session or session['{}_expires_at'.format(name)] <
            datetime.now().strftime('%s'))

    def validate_or_set_super_token(self):
        """Set top level access token in session."""

        if self.is_invalid_token('access_token'):
            token_info = Auth.get_backend_token(
                client_id=settings.MAILMOJO['CLIENT_ID'],
                client_secret=settings.MAILMOJO['CLIENT_SECRET'],
                scope='embed_newsletter_creation'
            )

            if not token_info.get('access_token'):
                raise Http404

            self.set_token_in_session('access_token', token_info)

    def validate_or_set_user_token(self, username):
        """Set user access token in session."""

        session = self.request.session

        if self.is_invalid_token('ti_access_token'):
            token_info = Auth.get_legacy_token(
                client_id=settings.MAILMOJO['CLIENT_ID'],
                client_secret=settings.MAILMOJO['CLIENT_SECRET'],
                username=username,
                password=session['access_token']
            )

            self.set_token_in_session('ti_access_token', token_info)


class NamedSuccessUrlMixin(object):
    def get_success_url(self):
        url = reverse(self.success_url)
        return url
