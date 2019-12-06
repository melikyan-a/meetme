from os import path
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from users.models import MeetUser
from django.conf import settings


class EventCategory(models.Model):

    E_TYPES = (
        ('0', _('Other')),
        ('1', _('Sport')),
        ('2', _('Education')),
        ('3', _('Volunteering')),
        ('4', _('Relax')),
        ('5', _('Politic')),
    )

    name = models.CharField(choices=E_TYPES, max_length=30, blank=False, unique=True, verbose_name=_('Title'))

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.get_name_display()


class ActualEventManager(models.Manager):
    def get_queryset(self):
        # hurry_time = timezone.timedelta(hours=2)
        now_time = timezone.now()
        return super(ActualEventManager, self).get_queryset().filter(dt__lte=now_time, is_active=True)


class Event(models.Model):
    id = models.AutoField(primary_key=True)
    today = timezone.now
    name = models.CharField(verbose_name=_('Title'), max_length=30, blank=False, default=_('Sabantuy'))
    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE,
                                 verbose_name=_('Event Category'), default='0')
    dt = models.DateTimeField(blank=False, verbose_name=_('Date and time of the event'), default=today)
    is_active = models.BooleanField(default=True, verbose_name=_('Show to users?'))
    objects = models.Manager()
    current_events = ActualEventManager()
    image = models.ImageField(max_length=127, verbose_name=_('Event, Image'),
                              upload_to=path.join('event', 'image'), default='./event/image/default_event.jpg')

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('Events')
        unique_together = ('name', 'dt',)

    def __str__(self):
        return str(self.id)

    def get_image(self):
        return settings.SITE_URL + self.image.url


class UserEvent(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(MeetUser, related_name='liked_events', on_delete=models.CASCADE, verbose_name=_("Owner"))
    liked_events = models.ManyToManyField(Event, verbose_name=_('Liked events'))

    class Meta:
        verbose_name = _('liked event')
        verbose_name_plural = _('Liked events')

    def __str__(self):
        return self.owner.username

