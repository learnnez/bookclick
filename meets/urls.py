from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy

import meets.views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url=reverse_lazy('home-view'))),                              
    url(r'^booking/home/$', meets.views.HomeView.as_view(), name='home-view',), 
    url(r'^booking/list/$', meets.views.ListMeetView.as_view(), name='meets-list',),
    url(r'^booking/list/(?P<year>\d{4})/(?P<month>\d{1,2})$', meets.views.DayMonthMeetView.as_view(), name='meets-month',),
    url(r'^booking/list/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})$', meets.views.DayMonthMeetView.as_view(), name='meets-day',),
    url(r'^booking/new/$', meets.views.CreateMeetView.as_view(), name='meets-new',),
    url(r'^booking/view/(?P<pk>\d+)/$', meets.views.MeetView.as_view(), name='meets-view',),
    url(r'^booking/edit/(?P<pk>\d+)/$', meets.views.UpdateMeetView.as_view(), name='meets-edit',),
    url(r'^booking/delete/(?P<pk>\d+)/$', meets.views.DeleteMeetView.as_view(), name='meets-delete',),
) 

urlpatterns += patterns('',
    url(r'^logout/$', meets.views.LogoutView.as_view(), name='bookapp-logout'),
    url(r'^login/$', meets.views.LoginView.as_view(), name='bookapp-login'),
    url(r'^password_reset/$', meets.views.PasswordResetView.as_view(), name='bookapp-password-reset'),
    url(r'^register/$', meets.views.CreateUser.as_view(), name='bookapp-register'),
)

urlpatterns += patterns('',
    url(r'^venue/list/$', meets.views.VenueViewList.as_view(), name='venue-list',),
    url(r'^venue/new/$', meets.views.VenueViewCreate.as_view(), name='venue-new',),
    url(r'^venue/view/(?P<code>\w+)/$', meets.views.VenueView.as_view(), name='venue-view',),
    url(r'^venue/edit/(?P<code>\w+)/$', meets.views.VenueViewUpdate.as_view(), name='venue-edit',),
    url(r'^venue/delete/(?P<code>\w+)/$', meets.views.VenueViewDelete.as_view(), name='venue-delete',),
)

    
