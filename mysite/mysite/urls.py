from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from mysite import settings

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
    url(r'^SimpleHTMLTables/', 'scisheets.views.simple_html_tables'),
    url(r'^upload/', 'scisheets.views.upload'),
    #url(r'^scisheets/', 'scisheets.views.scisheets'),
    url(r'^scisheets/(?P<ncol>.+)/(?P<nrow>.+)/$', 'scisheets.views.scisheets'),
    url(r'^scisheets/(?P<ncol>.+)/(?P<nrow>.+)/command', 'scisheets.views.scisheets_command'),
    url(r'^scisheets/$', 'scisheets.views.scisheets_reload'),
    url(r'^scisheets/command', 'scisheets.views.scisheets_command0'),
    url(r'^tryajax/scisheets_command', 'scisheets.views.tryajax_reply'),
    url(r'^tryajax', 'scisheets.views.tryajax'),
)
urlpatterns += staticfiles_urlpatterns()
