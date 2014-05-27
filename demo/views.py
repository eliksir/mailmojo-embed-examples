from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView

from . import forms
from . import utils
from .mixins import NamedSuccessUrlMixin, TokenMixin


class IntegrationView(NamedSuccessUrlMixin, TokenMixin, FormView):
    def form_valid(self, form):
        # Embed options
        self.request.session['options'] = {
            'lang': form.cleaned_data.get('lang'),
            'css': form.cleaned_data.get('css'),
            'skip_recipients_step': form.cleaned_data.get('skip_recipients_step'),
        }
        return super(IntegrationView, self).form_valid(form)

    def get_redirect_uri(self):
        """Return redirect URI."""
        return self.request.build_absolute_uri('/')[:-1]


class HomeView(IntegrationView):
    template_name = 'home.html'
    form_class = forms.TransparentIntegrationForm
    success_url = 'embed'

    def get(self, *args, **kwargs):
        """Handles creating super token and token for given user."""
        self.validate_or_set_super_token()

        if self.request.session.get('version') != settings.VERSION:
            # Make sure we remove previously stored access tokens when we have a
            # version update
            return redirect('force-update')

        code = self.request.GET.get('code')
        # Retrieve access token from given code
        if code:
            token_info = utils.get_access_token_from_code(code,
                redirect_uri=self.get_redirect_uri())
            self.set_user_token(token_info)
            return redirect('embed')

        return super(HomeView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super(HomeView, self).get_context_data(**kwargs)
        data['login_int_form'] = forms.LoginIntegrationForm()
        return data

    def form_valid(self, form):
        self.validate_or_set_user_token(form.cleaned_data.get('username'))
        return super(HomeView, self).form_valid(form)


class LoginIntegrationView(IntegrationView):
    template_name = 'home.html'
    form_class = forms.LoginIntegrationForm

    def get_success_url(self):
        return utils.get_auth_grant_url(redirect_uri=self.get_redirect_uri())


class ForceUpdateView(View):
    def get(self, *args, **kwargs):
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

