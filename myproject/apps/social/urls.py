from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from myproject.apps.social import views as social

urlpatterns = patterns("",
    url(r'^insertjson/$', social.UploadView.as_view(), name='insertjson'),
    url(r'^(?P<biz_id>\d+)/post/$', social.PostView.as_view(), name='social_post'),
    url(r'^(?P<biz_id>\d+)/post/json/$', social.FacebookJsonResponse.as_view(),
                                                name='facebook_json_response'),
    url(r'^post/edit/(?P<post_id>\d+)/$', social.EditAjaxPostView.as_view(),
                                                        name='ajax_edit_post'),
    url(r'^accounts/$', social.AccountsView.as_view(), name='social_accounts'),
    url(r'^settings/$', social.SettingsView.as_view(), name='social_settings'),
)






