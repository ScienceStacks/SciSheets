from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from mysite import settings
import scisheets.views

urlpatterns = [
    url(r'^deletetable/', scisheets.views.deletetable),
    url(r'^hello/(?P<name>.+)/$', scisheets.views.hello),
    url(r'^maketable/', scisheets.views.maketable),
    url(r'^nested/', scisheets.views.nested),
    url(r'^plot/(?P<filename>.+)/$', scisheets.views.plot),
    url(r'^tables/(?P<node>.+)/$', scisheets.views.tables),
    url(r'^upload/', scisheets.views.upload),
    url(r'^tryajax/scisheets_command', scisheets.views.tryajax_reply),
    url(r'^tryajax', scisheets.views.tryajax),
    # URLs used in scisheets
    # Used to generate a scitable
    url(r'^scisheets/(?P<ncol>.+)/(?P<nrow>.+)/$', scisheets.views.scisheets),
    # URL to load a previously created table
    url(r'^scisheets/$', scisheets.views.scisheets_reload),
    # URL used by Ajax passing arguments as GET parameters
    url(r'^scisheets/command', scisheets.views.scisheets_command0),
    url(r'^admin/', include(admin.site.urls)),
]
#urlpatterns += staticfiles_urlpatterns()
