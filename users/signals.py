from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
UserModel = get_user_model()


@receiver(post_save, sender=UserModel)
def add_facebook_profile_link(sender, instance, created, **kwargs):
    if instance.pk:
        user = UserModel.objects.get(pk=instance.pk)
        data = user.social_auth.all().values('extra_data')[0]
        user.link = data['extra_data']['link']
        user.save()