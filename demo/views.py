from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import messages as msg
from django.shortcuts import Http404, redirect, render

from . import utils
from .forms import EmbedForm


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


def home(request):
    """Handles creating super token and token for given user."""
    _validate_or_set_super_token(request)

    if request.session.get('version') != settings.VERSION:
        # Make sure we remove previously stored access tokens when we have a
        # version update
        return redirect('force-update')

    code = request.GET.get('code')
    # Retrice access token from given code
    if code:
        token_info = utils.get_access_token_from_code(code,
            redirect_uri=_get_redirect_uri(request))
        _set_user_token(request, token_info)
        return redirect('newsletter')

    if request.POST:
        form = EmbedForm(request.POST)

        if form.is_valid():
            # Embed options
            request.session['options'] = {
                'lang': form.cleaned_data['lang'],
                'css': form.cleaned_data['css'],
                'skip_recipients_step': form.cleaned_data['skip_recipients_step'],
            }

            # Redirect to authorize to retrieve a code
            if form.cleaned_data.get('auth_code_grant'):
                url = utils.get_auth_grant_url(
                        redirect_uri=_get_redirect_uri(request))
                return redirect(url)

            _validate_or_set_user_token(request, form.cleaned_data['username'])
            return redirect('newsletter')
    else:
        form = EmbedForm()
    return render(request, 'home.html', {'form': form})


def force_update(request):
    """Removes all access tokens and expire dates in session."""
    request.session.flush()
    request.session['version'] = settings.VERSION
    return redirect('home')


def newsletter(request):
    """Open iframe with embed newsletter for given user."""
    user_access_token = request.session.get('user_access_token')
    if not user_access_token:
        return redirect('home')

    embed_url = utils.get_embed_url(user_access_token,
                                    ip=request.META['REMOTE_ADDR'],
                                    options=request.session.get('options'))
    return render(request, 'newsletter.html', {
        'embed_url': embed_url
    })
