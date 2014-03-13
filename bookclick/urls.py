from django.conf.urls import patterns, include, url
import meets.views  
from django.contrib import admin
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bookclick.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
   
    url(r'^$', RedirectView.as_view(url=reverse_lazy('bookapp-login'))),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('meets.urls')),
    url(r'^captcha/', include('captcha.urls')),
)


