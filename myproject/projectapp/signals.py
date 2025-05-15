from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from .models import UserProfile

@receiver(user_signed_up)
def create_profile_for_new_user(request, user, **kwargs):
    UserProfile.objects.create(user=user, is_admin=True)