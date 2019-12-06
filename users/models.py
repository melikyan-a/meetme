from os import path
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, PermissionsMixin, AbstractBaseUser
)
from django.contrib.auth.models import Group as BaseGroup
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.utils import timezone
from django.conf import settings


class MeetmeUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        # if not email:
        #     raise ValueError('The given email must be set')
        # username = self.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, password, **extra_fields)


class AbstractCUser(AbstractBaseUser, PermissionsMixin):

    NOT = 'empty'
    MALE = 'male'
    FEMALE = 'female'

    SEX = (
        (NOT, _('Empty')),
        (MALE, _('Male')),
        (FEMALE, _('Female')),
    )

    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(verbose_name=_('email address'), null=True, blank=True)
    first_name = models.CharField(_('first name'), max_length=50, null=True, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, null=True, blank=True)
    sex = models.CharField(max_length=6, choices=SEX, default='empty', verbose_name=_('Gender'))
    is_subscriber = models.BooleanField(default=False, verbose_name=_('Is news subscriber'))

    avatar = models.ImageField(max_length=127, verbose_name=_('Profile photo'),
                               upload_to=path.join('user', 'logo'), default='./user/logo/default.png')

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_seen = models.DateTimeField(auto_now_add=True)

    objects = MeetmeUserManager()

    USERNAME_FIELD = 'username'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('Users')
        abstract = True

    def __str__(self):
        return str(self.email)

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def get_avatar(self):
        return settings.SITE_URL + self.avatar.url

    def avatar_tag(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % self.get_avatar())

    avatar_tag.short_description = _('Avatar')


class MeetUser(AbstractCUser):
    class Meta(AbstractCUser.Meta):
        swappable = 'AUTH_USER_MODEL'


# This code is triggered whenever a new user has been created and saved to the database
@receiver(post_save, sender=MeetUser)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


# Base Group model
class Group(BaseGroup):
    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('Groups')
        proxy = True


class LikeUser(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(MeetUser, related_name='liked_user', on_delete=models.CASCADE, verbose_name=_("Owner"))
    liked = models.ManyToManyField(MeetUser, verbose_name=_('Like with'))

    class Meta:
        verbose_name = _('liked user')
        verbose_name_plural = _('Liked users')

    def __str__(self):
        return self.owner.username


class DislikeUser(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(MeetUser, related_name='disliked_user', on_delete=models.CASCADE, verbose_name=_("Owner"))
    disliked = models.ManyToManyField(MeetUser, verbose_name=_('Dislike with'))

    class Meta:
        verbose_name = _('disliked user')
        verbose_name_plural = _('Disliked users')

    def __str__(self):
        return self.owner.username