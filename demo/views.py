from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import messages as msg
from django.shortcuts import Http404, redirect
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView

from . import utils
from .forms import EmbedForm
from .mixins import NamedSuccessUrlMixin


### HELPER FUNCTIONS ####


def _set_token_in_session(session, name, token_info):
    session[name] = token_info['access_token']
    session['{}_expires_at'.format(name)] = (datetime.now() +
            timedelta(seconds=token_info['expires_in'])).strftime('%s')


def _validate_or_set_super_token(request):
    """Set top level access token in session."""
    session = request.session
    if ('access_token' not in session or
            session['access_token_expires_at'] < datetime.now().strftime('%s')):
        token_info = utils.get_access_token()
        if not token_info.get('access_token'):
            raise Http404

        _set_token_in_session(session, 'access_token', token_info)


def _validate_or_set_user_token(request, username):
    """Set user access token in session."""
    session = request.session
    if ('user_access_token' not in session or
            session['user_access_token_expires_at'] < datetime.now().strftime('%s')):
        token_info = utils.get_user_access_token(username, token=session['access_token'])
        _set_user_token(request, token_info)


def _set_user_token(request, token_info):
    if not token_info.get('access_token'):
        msg.error(request, "Error: {}".format(token_info.get('error')))
        return False

    _set_token_in_session(request.session, 'user_access_token', token_info)


def _get_redirect_uri(request):
    return request.build_absolute_uri('/')[:-1]


#### VIEWS ####


class HomeView(NamedSuccessUrlMixin, FormView):
    template_name = 'home.html'
    form_class = EmbedForm
    success_url = 'embed'

    def get(self, *args, **kwargs):
        """Handles creating super token and token for given user."""
        _validate_or_set_super_token(self.request)

        if self.request.session.get('version') != settings.VERSION:
            # Make sure we remove previously stored access tokens when we have a
            # version update
            return redirect('force-update')

        code = self.request.GET.get('code')
        # Retrieve access token from given code
        if code:
            token_info = utils.get_access_token_from_code(code,
                redirect_uri=_get_redirect_uri(self.request))
            _set_user_token(self.request, token_info)
            return redirect('embed')

        return super(HomeView, self).get(*args, **kwargs)

    def form_valid(self, form):
        # Embed options
        self.request.session['options'] = {
            'lang': form.cleaned_data['lang'],
            'css': form.cleaned_data['css'],
            'skip_recipients_step': form.cleaned_data['skip_recipients_step'],
        }

        # Redirect to authorize to retrieve a code
        if form.cleaned_data.get('auth_code_grant'):
            url = utils.get_auth_grant_url(
                    redirect_uri=_get_redirect_uri(self.request))
            return redirect(url)

        _validate_or_set_user_token(self.request, form.cleaned_data['username'])
        return super(HomeView, self).form_valid(form)


class ForceUpdateView(View):
    def post(self, *args, **kwargs):
        """Removes all access tokens and expire dates in session."""
        self.request.session.flush()
        self.request.session['version'] = settings.VERSION
        return redirect('home')


class EmbedView(TemplateView):
    """Open iframe with embed newsletter for given user."""
    template_name = 'newsletter.html'

    def get_context_data(self, **kwargs):
        data = super(EmbedView, self).get_context_data(**kwargs)

        user_access_token = self.request.session.get('user_access_token')
        if not user_access_token:
            return redirect('home')

        embed_url = utils.get_embed_url(user_access_token,
                ip=self.request.META['REMOTE_ADDR'],
                options=self.request.session.get('options'))
        data['embed_url'] = embed_url
        return data

