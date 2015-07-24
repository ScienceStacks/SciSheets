from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^codons/', 'scisheets.views.codons'),
    url(r'^hello/', 'scisheets.views.hello'),
    url(r'^letter/', 'scisheets.views.letter'),
    url(r'^plot/(?P<filename>.+)/$', 'scisheets.views.plot'),
    url(r'^upload/', 'scisheets.views.upload'),
    url(r'^maketable/', 'scisheets.views.maketable'),
    url(r'^deletetable/', 'scisheets.views.deletetable'),
    url(r'^query/', 'heatmap.views.query'),
    url(r'^nested/', 'scisheets.views.nested'),
    url(r'^tables/(?P<node>.+)/$', 'scisheets.views.tables'),
)
urlpatterns += staticfiles_urlpatterns()
