from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_groups(sender, **kwargs):
    if sender.label != "works":
        return
   
    Group.objects.get_or_create(name="Author")
    Group.objects.get_or_create(name="Consumer")