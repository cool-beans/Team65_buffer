from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'app.views.home', name='home'),
   #############################################################
   # Main Navigation
   #############################################################
    url(r'^about/$', 'app.views.about', name='about'),
    url(r'^programs/$', 'app.views.programs', name='programs'),
    #log in
    url(r'^login', 'django.contrib.auth.views.login', {'template_name':'final_project/login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^register/$', 'app.views.register', name='register'),
   # Programs
    url(r'^program_profile/(?P<program_id>\d+)$', 'app.views.program_profile', name='program_profile'),#should be the individual program
    url(r'^program_create/$', 'app.views.program_create', name='program_create'),
    url(r'^program_edit/(?P<program_id>\d+)$', 'app.views.program_edit', name='program_edit'),

   # Members
    url(r'^members/$', 'app.views.members', name='members'),
    url(r'^member_profile/(?P<member_id>\d+)$', 'app.views.member_profile', name='member_profile'),
    url(r'^filter_members/(?P<program_id>\d+)$', 'app.views.filter_members', name='filter_members'),
    url(r'^member_edit/(?P<member_id>\d+)$', 'app.views.member_edit', name='member_edit'),

   # Events
    url(r'^events/$','app.views.events', name='events'),
    url(r'^event_profile/$', 'app.views.event_profile', name='event_profile'),
    url(r'^event_create/$', 'app.views.event_create', name='event_create'),
#    url(r'^filter_events/(?P<event_id>\d+)$', 'app.views.filter_events', name='filter_events'),
    url(r'^event_edit/(?P<event_id>\d+)$', 'app.views.event_edit', name='event_edit'),
)
