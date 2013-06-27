from django.conf.urls.defaults import *
from django.conf import settings
from myproject.apps.reports import views as report

urlpatterns = patterns("",
    url(r"^(?P<biz_id>\d+)/$",          report.Overview.as_view(),     name="reports_overview"),
    url(r"^(?P<biz_id>\d+)/social/$",   report.Social.as_view(),       name="reports_social"),
    url(r"^(?P<biz_id>\d+)/ratings/$",  report.Ratings.as_view(),      name="reports_ratings"),
    url(r'^(?P<biz_id>\d+)/twitter/$',  report.TwitterView.as_view(),  name="reports_twitter"),
    url(r'^(?P<biz_id>\d+)/facebook/$', report.FacebookView.as_view(), name="reports_facebook"),
    url(r'^(?P<biz_id>\d+)/mailchimp/$',report.MailchimpView.as_view(),name="reports_mailchimp"),
)

