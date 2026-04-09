import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('worker', 'Worker'),
        ('admin', 'Admin'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('banned', 'Banned'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def is_active_user(self):
        return self.status == 'active'

    def __str__(self):
        return f"{self.username} ({self.role})"

class Profile(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    nickname = models.CharField(max_length=50, null=True, blank=True)
    realName = models.CharField(max_length=50, null=True, blank=True)
    countrie = models.CharField(max_length=50, null=True, blank=True)
    level = models.PositiveIntegerField(null=True, blank=True, default=0)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    userState = models.CharField(max_length=50, null=False, blank=False)

    avatar = models.URLField(default="https://i.pinimg.com/236x/d4/74/1c/d4741cb779ddec6509ca1ae0cb137a7d.jpg")
    frame = models.URLField(default="https://cdn.fastly.steamstatic.com/steamcommunity/public/images/items/860950/6e1b5f5977036a189465f5455f2c54722c12883d.png")
    background = models.URLField(default="https://w.wallhaven.cc/full/9o/wallhaven-9o687w.png")

    def save(self, *args, **kwargs):
        if not self.nickname:
            self.nickname = self.user.username
        if not self.userState:
            self.userState = self.user.status
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Profile of {self.user.username}"