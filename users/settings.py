from django.conf import settings
from django.utils.translation import ugettext_lazy as _

MEETUSER_SETTINGS = {
    'app_verbose_name': _("Users"),
    'register_proxy_auth_group_model': False,
}

if hasattr(settings, 'USERS'):
    MEETUSER_SETTINGS.update(settings.MEETUSER)