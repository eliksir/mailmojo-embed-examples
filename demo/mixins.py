from django.core.urlresolvers import reverse


class NamedSuccessUrlMixin(object):
    def get_success_url(self):
        url = reverse(self.success_url)
        return url
