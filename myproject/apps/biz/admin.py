from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from guardian.admin import GuardedModelAdmin

from myproject.apps.biz.models import Business, Website, WebsiteTypes


class BusinessAdmin(GuardedModelAdmin): pass
class WebsiteAdmin(GuardedModelAdmin): pass
class WebsiteTypesAdmin(GuardedModelAdmin): pass

admin.site.register(Business, BusinessAdmin)
admin.site.register(Website, WebsiteAdmin)
admin.site.register(WebsiteTypes, WebsiteTypesAdmin)
