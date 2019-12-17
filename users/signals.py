from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
UserModel = get_user_model()


@receiver(pre_save, sender=UserModel)
def add_facebook_profile_link(sender, instance, created, **kwargs):
    if created:
        data = instance.social_auth.all().values('extra_data')[0]
        instance.link = data['extra_data']['link']
        instance.save()