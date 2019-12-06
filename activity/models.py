from os import path
from django.db import models
from event.models import EventCategory
from django.utils.translation import ugettext_lazy as _
from users.models import MeetUser
from django.conf import settings


# Create your models here.

class ActualActivityManager(models.Manager):
    def get_queryset(self):
        return super(ActualActivityManager, self).get_queryset().filter(is_active=True)


class Activity(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, blank=False, default=_('Flash mob'), unique=True, verbose_name=_('Title'))
    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE,
                                 verbose_name=_('Event Category'), default='0')
    is_active = models.BooleanField(default=True, verbose_name=_('Show to users?'))
    objects = models.Manager()  # The default manager.
    current_activities = ActualActivityManager()  # only active activities
    image = models.ImageField(max_length=127, verbose_name=_('Activity, Image'),
                              upload_to=path.join('activity', 'image'), default='./activity/image/default_activity.jpg')

    class Meta:
        verbose_name = _('activity')
        verbose_name_plural = _('Activities')

    def __str__(self):
        return str(self.id)

    def get_image(self):
        return settings.SITE_URL + self.image.url


class UserActivity(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(MeetUser, related_name='liked_activities', on_delete=models.CASCADE, verbose_name=_("Owner"))
    liked_activities = models.ManyToManyField(Activity, verbose_name=_('Liked activities'))

    class Meta:
        verbose_name = _('liked activity')
        verbose_name_plural = _('Liked activities')

    def __str__(self):
        return self.owner.username



