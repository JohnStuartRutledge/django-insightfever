from django.conf.urls.defaults import *
from django.conf import settings
from myproject.apps.likeriser import views

urlpatterns = patterns("",
    url(r'^(?P<biz_id>\d+)/$', 
        views.LikeriserView.as_view(),  name="likeriser_view"),
)

