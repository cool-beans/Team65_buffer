from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^final_project/', include('app.urls')),
    url(r'^$', 'app.views.common.home', name='home'),
)
