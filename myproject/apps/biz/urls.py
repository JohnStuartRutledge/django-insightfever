"""
URL patterns for the business pages 
"""
from django.conf.urls.defaults import *
from django.conf import settings
from myproject.apps.biz import views as biz_views
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$',                          biz_views.biz_roldex,   name='biz_roldex'  ),
    url(r'^new/$',                      biz_views.biz_new,      name='biz_new'     ),
    url(r'^(?P<biz_id>\d+)/$',          biz_views.biz_details,  name='biz_details' ),
    url(r'^(?P<biz_id>\d+)/edit/$',     biz_views.biz_edit,     name='biz_edit'    ),
    url(r'^(?P<biz_id>\d+)/websites/$', biz_views.biz_websites, name='biz_websites'),
#   url(r'^(?P<biz_id>\d+)/accounts/$', biz_views.biz_accounts, name='biz_accounts'),
    url(r'^accounts/route/$',           biz_views.biz_route,    name='biz_route'   ),
    url(r'^(?P<biz_id>\d+)/accounts/done/$', biz_views.biz_done,name='biz_done'    ),
)

