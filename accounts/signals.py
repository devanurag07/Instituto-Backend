from accounts.models import User
from institute.models import StudentProfile
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if(created):
        role = instance.role
        if(instance.role.lower() == "student"):
            StudentProfile.objects.create(user=instance)
            print("Profile Created")
