from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group as StockGroup
from django.utils.translation import ugettext_lazy as _
from users.forms import UserChangeForm, UserCreationForm
from users.settings import MEETUSER_SETTINGS
from .models import *


@admin.register(MeetUser)
class UserAdmin(BaseUserAdmin):
    add_form_template = 'admin/add_form.html'
    fieldsets = (
        (None, {'fields': ('username', 'password', 'email')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'sex', 'is_subscriber', 'avatar')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('username', 'avatar_tag', 'first_name', 'last_name', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_superuser', 'is_staff', 'is_subscriber')
    ordering = ('username',)


if MEETUSER_SETTINGS['register_proxy_auth_group_model']:
    admin.site.unregister(StockGroup)

    @admin.register(Group)
    class GroupAdmin(BaseGroupAdmin):
        pass


# @admin.register(LikeUser)
# class LikeUserAdmin(admin.ModelAdmin):
#     list_display = ('id', 'owner')
#
#
# @admin.register(DislikeUser)
# class DislikeUserAdmin(admin.ModelAdmin):
#     list_display = ('id', 'owner')