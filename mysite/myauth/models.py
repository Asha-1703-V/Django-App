from django.db import models
from django.contrib.auth.models import User

def user_avatar_directory_path(instance, filename):
    return "users/user_{pk}/avatar/{filename}".format(
        pk=instance.user.pk,
        filename=filename,
    )

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    agreement_accepted = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to=user_avatar_directory_path, null=True, blank=True)
