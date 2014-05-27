from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView

from . import utils
from .forms import EmbedForm
from .mixins import NamedSuccessUrlMixin, TokenMixin


class HomeView(NamedSuccessUrlMixin, TokenMixin, FormView):
    template_name = 'home.html'
    form_class = EmbedForm
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

    def form_valid(self, form):
        # Embed options
        self.request.session['options'] = {
            'lang': form.cleaned_data['lang'],
            'css': form.cleaned_data['css'],
            'skip_recipients_step': form.cleaned_data['skip_recipients_step'],
        }

        username = form.cleaned_data.get('username')
        # Redirect to authorize endpoint to retrieve a code
        if not username:
            url = utils.get_auth_grant_url(redirect_uri=self.get_redirect_uri())
            return redirect(url)

        self.validate_or_set_user_token(username)
        return super(HomeView, self).form_valid(form)

    def get_redirect_uri(self):
        """Return redirect URI."""
        return self.request.build_absolute_uri('/')[:-1]


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

