from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^codons/', 'scisheets.views.codons'),
    url(r'^deletetable/', 'scisheets.views.deletetable'),
    url(r'^hello/', 'scisheets.views.hello'),
    url(r'^letter/', 'scisheets.views.letter'),
    url(r'^maketable/', 'scisheets.views.maketable'),
    url(r'^nested/', 'scisheets.views.nested'),
    url(r'^plot/(?P<filename>.+)/$', 'scisheets.views.plot'),
    url(r'^query/', 'heatmap.views.query'),
    url(r'^tables/(?P<node>.+)/$', 'scisheets.views.tables'),
    url(r'^testhtmltable/', 'scisheets.views.test_html_table'),
    url(r'^upload/', 'scisheets.views.upload'),
)
urlpatterns += staticfiles_urlpatterns()
