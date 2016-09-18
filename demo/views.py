from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView

from demo import forms, mixins
from mm import Auth, EmbedSession


class IntegrationViewMixin(object):
    def get_redirect_uri(self):
        """Return redirect URI."""
        return self.request.build_absolute_uri('/')[:-1]


class HomeView(IntegrationViewMixin,
               mixins.TokenMixin,
               mixins.NamedSuccessUrlMixin,
               FormView):

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
            token_info = Auth.get_web_token(
                client_id=settings.MAILMOJO['CLIENT_ID'],
                client_secret=settings.MAILMOJO['CLIENT_SECRET'],
                code=code,
                redirect_uri=self.get_redirect_uri(),
                state=self.request.GET.get('state'),
            )
            self.set_token_in_session('li_access_token', token_info)
            return redirect('login-int-embed')

        return super(HomeView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super(HomeView, self).get_context_data(**kwargs)
        data['login_int_form'] = forms.LoginIntegrationForm()
        return data

    def form_valid(self, form):
        self.request.session['ti_options'] = {
            'locale': form.cleaned_data.get('locale'),
            'enable_theme': form.cleaned_data.get('enable_theme'),
            'enable_newsletters_index': form.cleaned_data.get(
                'enable_newsletters_index'),
        }

        self.validate_or_set_super_token()
        self.validate_or_set_user_token(form.cleaned_data.get('username'))
        return super(HomeView, self).form_valid(form)


class LoginIntegrationView(IntegrationViewMixin,
                           mixins.TokenMixin,
                           mixins.NamedSuccessUrlMixin,
                           FormView):

    template_name = 'home.html'
    form_class = forms.LoginIntegrationForm
    success_url = 'login-int-embed'

    def form_valid(self, form):
        self.request.session['li_options'] = {
            'locale': form.cleaned_data.get('locale'),
            'enable_theme': form.cleaned_data.get('enable_theme'),
            'enable_newsletters_index': form.cleaned_data.get(
                'enable_newsletters_index'),
        }
        return super(LoginIntegrationView, self).form_valid(form)

    def get_success_url(self):
        if self.is_invalid_token('li_access_token'):
            return Auth.get_authorization_url(
                client_id=settings.MAILMOJO['CLIENT_ID'],
                redirect_uri=self.get_redirect_uri(),
                scope=['embed']
            )

        return super(LoginIntegrationView, self).get_success_url()


class EmbedView(TemplateView):
    template_name = 'newsletter.html'
    access_token_key = None
    options_key = None

    def get_context_data(self, **kwargs):
        data = super(EmbedView, self).get_context_data(**kwargs)

        access_token = self.request.session.get(self.access_token_key)
        if not access_token:
            return redirect('home')

        embed_session = EmbedSession(
            access_token=access_token,
            session_type=EmbedSession.TYPE_NEWSLETTERS,
            user_ip=self.request.META['REMOTE_ADDR'],
            options=self.request.session.get(self.options_key),
        )
        embed = embed_session.create()
        data['embed'] = embed['content']

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
