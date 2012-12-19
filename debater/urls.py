from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'debater.views.home', name='home'),
    url(r'^data/(?P<collection>\w+)/$', 'debater.views.get', name='get_data'),
    url(r'^data/(?P<collection>\w+)/(?P<limit>\d+)$', 'debater.views.get', name='get_data'),
    url(r'^data/words/(?P<collection>\w+)/$', 'debater.views.words', name='get_words_bare'),
    url(r'^data/words/(?P<collection>\w+)/(?P<begin>\d+)/(?P<end>\d+)$', 'debater.views.words', name='get_words'),
    # url(r'^crum/', include('crum.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)