from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'app.views.home', name='home'),
   #############################################################
   # Main Navigation
   #############################################################
    url(r'^about/$', 'app.views.about', name='about'),
    url(r'^programs/$', 'app.views.programs', name='programs'),
    #log in
   url(r'^login/$', 'django.contrib.auth.views.login', {'template_name':'app/login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^register/$', 'app.views.register', name='register'),
   # Programs
    url(r'^program_profile/$', 'app.views.program_profile', name='program_profile'),#should be the individual program

   # Members
    url(r'^members/$', 'app.views.members', name='members'),
    url(r'^member_profile/$', 'app.views.member_profile', name='member_profile'),
)
