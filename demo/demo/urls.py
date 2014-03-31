from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'demo.views.home', name='home'),
    url(r'^newsletter/$', 'demo.views.newsletter', name='newsletter'),
)
