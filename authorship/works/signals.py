# works/signals.py
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from works.models import Work

@receiver(post_migrate)
def assign_works_permissions(sender, **kwargs):
    if sender.label != "works":
        return

    try:
        author_group = Group.objects.get(name="Author")
        consumer_group = Group.objects.get(name="Consumer")
    except Group.DoesNotExist:
        return

    content_type = ContentType.objects.get_for_model(Work)

    add_work = Permission.objects.get(codename="add_work", content_type=content_type)
    change_work = Permission.objects.get(codename="change_work", content_type=content_type)
    delete_work = Permission.objects.get(codename="delete_work", content_type=content_type)
    view_work = Permission.objects.get(codename="view_work", content_type=content_type)

    author_group.permissions.add(add_work, view_work, change_work, delete_work)
    consumer_group.permissions.add(view_work)