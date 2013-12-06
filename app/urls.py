from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'app.views.common.home', name='home'),
   #############################################################
   # Main Navigation
   #############################################################
    url(r'^about/$', 'app.views.common.about', name='about'),
    url(r'^programs/$', 'app.views.programs.all', name='programs'),
    #log in
    url(r'^login', 'django.contrib.auth.views.login', {'template_name':'final_project/Members/login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^register/$', 'app.views.members.register', name='register'),
   # Programs
    url(r'^program_profile/(?P<program_id>\d+)$', 'app.views.programs.profile', name='program_profile'),#should be the individual program
    url(r'^program_create/$', 'app.views.programs.create', name='program_create'),
    url(r'^program_edit/(?P<program_id>\d+)$', 'app.views.programs.edit', name='program_edit'),

   # Members
    url(r'^members/$', 'app.views.members.all', name='members'),
    url(r'^search/$', 'app.views.members.search', name='search'),
    url(r'^member_profile/(?P<member_id>\d+)$', 'app.views.members.profile', name='member_profile'),
    url(r'^filter_members/(?P<program_id>\d+)$', 'app.views.members.filter', name='filter_members'),
    url(r'^member_edit/(?P<member_id>\d+)$', 'app.views.members.edit', name='member_edit'),

   # Events
    url(r'^events/$','app.views.events.all', name='events'),
    url(r'^event_profile/$', 'app.views.events.profile', name='event_profile'),
    url(r'^event_create/$', 'app.views.events.create', name='event_create'),
#    url(r'^filter_events/(?P<event_id>\d+)$', 'app.views.filter_events', name='filter_events'),
    url(r'^event_edit/$', 'app.views.events.edit', name='event_edit'),
   # Memberships
    url(r'^memberships/$','app.views.memberships.all', name='memberships'),
    url(r'^buy_membership/(?P<membership_type_id>\d+)$', 'app.views.memberships.buy', name='buy_membership'),
    url(r'^cancel_membership/(?P<membership_id>\d+)$', 'app.views.memberships.cancel', name='membership_cancel'),
    url(r'^create_membership_type/$', 'app.views.memberships.create_type', name='create_membership_type'),
    url(r'^edit_membership_type/(?P<membership_type_id>\d+)$', 'app.views.memberships.edit_type', name='edit_membership_type'),

)
