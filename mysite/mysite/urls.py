from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^codons/', 'jviz.views.codons'),
    url(r'^hello/', 'jviz.views.hello'),
    url(r'^letter/', 'jviz.views.letter'),
    url(r'^plot/(?P<filename>.+)/$', 'jviz.views.plot'),
    url(r'^upload/', 'jviz.views.upload'),
    url(r'^maketable/', 'jviz.views.maketable'),
    url(r'^deletetable/', 'jviz.views.deletetable'),
    url(r'^query/', 'jviz.views.query'),
    url(r'^nested/', 'jviz.views.nested'),
    url(r'^tables/(?P<node>.+)/$', 'jviz.views.tables'),
)
urlpatterns += staticfiles_urlpatterns()
