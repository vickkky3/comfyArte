from django.db import migrations

def create_groups_and_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    author_group, _ = Group.objects.get_or_create(name='Author')
    consumer_group, _ = Group.objects.get_or_create(name='Consumer')

    try:
        content_type = ContentType.objects.get(app_label='works', model='work')
        
    except ContentType.DoesNotExist:
        Work = apps.get_model('works', 'Work')
        content_type = ContentType.objects.get_for_model(Work)

    codenames = ['add_work', 'change_work', 'delete_work', 'view_work']
    permissions = {
        perm.codename: perm 
        for perm in Permission.objects.filter(content_type=content_type, codename__in=codenames)
    }

    for codename in codenames:
        if codename in permissions:
            author_group.permissions.add(permissions[codename])

    if 'view_work' in permissions:
        consumer_group.permissions.add(permissions['view_work'])

def remove_groups_and_permissions(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('works', '__latest__'),
        ('contenttypes', '__latest__'),
        ('auth', '__latest__'),
    ]

    operations = [
        migrations.RunPython(create_groups_and_permissions, remove_groups_and_permissions),
    ]