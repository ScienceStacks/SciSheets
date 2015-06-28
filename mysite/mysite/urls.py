from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^heatmap/hello/', 'heatmap.views.hello'),
    url(r'^heatmap/letter/', 'heatmap.views.letter'),
    url(r'^heatmap/plot/(?P<filename>.+)/$', 'heatmap.views.plot'),
    url(r'^heatmap/upload/', 'heatmap.views.upload'),
    url(r'^heatmap/maketable/', 'heatmap.views.maketable'),
    url(r'^heatmap/deletetable/', 'heatmap.views.deletetable'),
    url(r'^heatmap/query/', 'heatmap.views.query'),
)
