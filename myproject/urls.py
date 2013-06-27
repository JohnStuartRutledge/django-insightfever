from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.views.generic.simple import redirect_to
from myproject.apps.profiles.forms import SignupFormExtra
from myproject import views
#from social_auth.views import associate, associate_complete, disconnect

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'myproject.views.home', name='home'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^grappelli/', include('grappelli.urls')),

    # OpenAuth URLS
    url(r'', include('social_auth.urls')),
    url(r'', include('banana_py.urls')),
    url(r'', include('debug_toolbar_user_panel.urls')),
    #(r'^facebook/', include('django_facebook.urls')), # django-facebook

    # override the signup form with usernea
    (r'^accounts/',  include('userena.urls')),
    (r'^accounts/signup/$', 'userena.views.signup', {'signup_form': SignupFormExtra}),
    (r'^messages/',  include('userena.contrib.umessages.urls')),
    (r'^knowledge/', include('knowledge.urls')),

    # testing
    url(r'^test/', views.TestView.as_view(), name='test_view'),

    # insightfever apps
    url(r'^dashboard/', 'myproject.views.dashboard', name='dashboard'),
    (r'^business/', include('myproject.apps.biz.urls')),
    (r'^reports/',  include('myproject.apps.reports.urls')),
    (r'^social/',   include('myproject.apps.social.urls')),
    (r'^likeriser/', include('myproject.apps.likeriser.urls')),
)
