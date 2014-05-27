from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView

from . import forms
from . import utils
from .mixins import NamedSuccessUrlMixin, TokenMixin


class IntegrationViewMixin(object):
    def get_redirect_uri(self):
        """Return redirect URI."""
        return self.request.build_absolute_uri('/')[:-1]


class HomeView(IntegrationViewMixin, NamedSuccessUrlMixin, TokenMixin,  FormView):
    template_name = 'home.html'
    form_class = forms.TransparentIntegrationForm
    success_url = 'transparent-int-embed'

    def get(self, *args, **kwargs):
        """Handles creating super token and token for given user."""
        # Make sure we remove previously stored access tokens when we have a
        # version update
        if self.request.session.get('version') != settings.VERSION:
            return redirect('force-update')

        # Retrieve access token from given code
        code = self.request.GET.get('code')
        if code:
            token_info = utils.get_access_token_from_code(code,
                redirect_uri=self.get_redirect_uri())
            self.set_token_in_session('li_access_token', token_info)
            return redirect('login-int-embed')

        return super(HomeView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super(HomeView, self).get_context_data(**kwargs)
        data['login_int_form'] = forms.LoginIntegrationForm()
        return data

    def form_valid(self, form):
        self.request.session['ti_options'] = {
            'lang': form.cleaned_data.get('lang'),
            'css': form.cleaned_data.get('css'),
            'skip_recipients_step': form.cleaned_data.get('skip_recipients_step'),
        }
        self.validate_or_set_super_token()
        self.validate_or_set_user_token(form.cleaned_data.get('username'))
        return super(HomeView, self).form_valid(form)


class LoginIntegrationView(IntegrationViewMixin, FormView):
    template_name = 'home.html'
    form_class = forms.LoginIntegrationForm

    def form_valid(self, form):
        self.request.session['li_options'] = {
            'lang': form.cleaned_data.get('lang'),
            'skip_recipients_step': form.cleaned_data.get('skip_recipients_step'),
        }
        return super(LoginIntegrationView, self).form_valid(form)

    def get_success_url(self):
        return utils.get_auth_grant_url(redirect_uri=self.get_redirect_uri())


class EmbedView(TemplateView):
    template_name = 'newsletter.html'
    access_token_key = None
    options_key = None

    def get_context_data(self, **kwargs):
        data = super(EmbedView, self).get_context_data(**kwargs)

        access_token = self.request.session.get(self.access_token_key)
        if not access_token:
            return redirect('home')

        embed_url = utils.get_embed_url(access_token,
                ip=self.request.META['REMOTE_ADDR'],
                options=self.request.session.get(self.options_key))
        data['embed_url'] = embed_url
        return data


class LoginIntegrationEmbedView(EmbedView):
    """Open iframe with embed newsletter for given user."""
    template_name = 'newsletter.html'
    access_token_key = 'li_access_token'
    options_key = 'li_options'


class TransparentIntegrationEmbedView(EmbedView):
    """Open iframe with embed newsletter for given user."""
    template_name = 'newsletter.html'
    access_token_key = 'ti_access_token'
    options_key = 'ti_options'


class ForceUpdateView(View):
    def get(self, *args, **kwargs):
        """Removes all access tokens and expire dates in session."""
        self.request.session.flush()
        self.request.session['version'] = settings.VERSION
        return redirect('home')
