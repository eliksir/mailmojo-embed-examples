from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns('',
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^login-integration/$', views.LoginIntegrationView.as_view(), name='login-int'),
    url(r'^newsletter/$', views.EmbedView.as_view(), name='embed'),
    url(r'^force-update/$', views.ForceUpdateView.as_view(), name='force-update'),
)
