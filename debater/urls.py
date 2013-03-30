from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'debater.views.home', name='home'),
    #url(r'^data/(?P<collection>\w+)/$', 'debater.views.get', name='get_data'),
    #url(r'^data/(?P<collection>\w+)/(?P<limit>\d+)$', 'debater.views.get', name='get_data'),
    #url(r'^data/words/(?P<collection>\w+)/$', 'debater.views.words', name='get_words_bare'),
    #url(r'^data/words/(?P<collection>\w+)/(?P<begin>\d+)/(?P<end>\d+)$', 'debater.views.words', name='get_words'),
    url(r'^(?P<collection>\w+)/(?P<begin>\d+)/(?P<end>\d+)/csv$', 'debater.views.to_csv', name='to_csv'),
)