from accounts.models import User
from institute.models import OwnerProfile, StudentProfile, TeacherProfile
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if(created):
        role = instance.role.lower()
        if(role == "student"):
            StudentProfile.objects.create(user=instance)
        elif(role == "owner"):
            OwnerProfile.objects.create(user=instance)

        else:
            pass
