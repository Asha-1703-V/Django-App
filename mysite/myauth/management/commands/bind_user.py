from django.contrib.auth.models import User, Group, Permission
from django.core.management import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
       user = User.objects.get(pk=4)
       group, created = Group.objects.get_or_create(
           name="profile_manager"
       )
       permissions_profile = Permission.objects.get(
           codename="view_profile"
       )
       permissions_logentry = Permission.objects.get(
           codename="view_logentry"
       )

       # добавление разрешения в группу
       group.permissions.add(permissions_profile)

       # присоединение пользователя к группе
       user.groups.add(group)

       # связать пользователя напрямую с разрешением
       user.user_permissions.add(permissions_logentry)

       group.save()
       user.save()