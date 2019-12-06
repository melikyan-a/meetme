from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from .models import *


# Register your models here.

class ActivityAdmin(admin.ModelAdmin):

    def image_tag(self, obj):
        return format_html('<img src="{}" width="120" height="120" />'.format(obj.image.url))

    image_tag.short_description = _('Activity Image')

    list_display = ('name', 'category', 'image_tag', 'is_active',)
    readonly_fields = ('image_tag',)


# @admin.register(UserActivity)
# class UserActivityAdmin(admin.ModelAdmin):
#     list_display = ('id', 'owner')


admin.site.register(Activity, ActivityAdmin)



