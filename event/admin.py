from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from .models import *


class EventAdmin(admin.ModelAdmin):

    def image_tag(self, obj):
        return format_html('<img src="{}" width="120" height="120" />'.format(obj.image.url))

    image_tag.short_description = _('Event Image')

    list_display = ('name', 'dt', 'category', 'image_tag', 'is_active',)
    readonly_fields = ('image_tag',)


class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


# @admin.register(UserEvent)
# class UserEventAdmin(admin.ModelAdmin):
#     list_display = ('id', 'owner')


admin.site.register(Event, EventAdmin)
admin.site.register(EventCategory, EventCategoryAdmin)

