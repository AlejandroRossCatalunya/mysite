from django.contrib.auth.models import User
from django.db import models


def avatar_directory_path(instance: "User", filename: str) -> str:
    return "users/avatars/user_{pk}/{filename}".format(
        pk=instance.user.pk,
        filename=filename
    )


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=1000, blank=True)
    agreement_accepted = models.BooleanField(default=False)
    avatar = models.ImageField(null=True, blank=True, upload_to=avatar_directory_path)

