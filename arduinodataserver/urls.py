from django.conf.urls.defaults import patterns, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    url('^$', 'arduinodataserver.views.index', name='arduinodataserver_index'),
    url('^meter/(\d+)/$', 'arduinodataserver.views.meter', name='arduinodataserver_meter'),
    url('^interval/(\d+)/json/$', 'arduinodataserver.views.interval_json', name='arduinodataserver_interval_json'),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
