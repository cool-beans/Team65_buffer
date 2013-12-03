from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'app.views-common.home', name='home'),
   #############################################################
   # Main Navigation
   #############################################################
    url(r'^about/$', 'app.views-common.about', name='about'),
    url(r'^programs/$', 'app.views-programs.programs', name='programs'),
    #log in
    url(r'^login', 'django.contrib.auth.views.login', {'template_name':'final_project/login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^register/$', 'app.views-members.register', name='register'),
   # Programs
    url(r'^program_profile/(?P<program_id>\d+)$', 'app.views-programs.program_profile', name='program_profile'),#should be the individual program
    url(r'^program_create/$', 'app.views-programs.program_create', name='program_create'),
    url(r'^program_edit/(?P<program_id>\d+)$', 'app.views-programs.program_edit', name='program_edit'),

   # Members
    url(r'^members/$', 'app.views-members.members', name='members'),
    url(r'^member_profile/(?P<member_id>\d+)$', 'app.views-members.member_profile', name='member_profile'),
    url(r'^filter_members/(?P<program_id>\d+)$', 'app.views-members.filter_members', name='filter_members'),
    url(r'^member_edit/(?P<member_id>\d+)$', 'app.views-members.member_edit', name='member_edit'),

   # Events
    url(r'^events/$','app.views-events.events', name='events'),
    url(r'^event_profile/$', 'app.views-events.event_profile', name='event_profile'),
    url(r'^event_create/$', 'app.views-events.event_create', name='event_create'),
#    url(r'^filter_events/(?P<event_id>\d+)$', 'app.views.filter_events', name='filter_events'),
    url(r'^event_edit/(?P<event_id>\d+)$', 'app.views-events.event_edit', name='event_edit'),
)
