from django.db import models

from main.constants import ACTION_TYPES, GENDER_TYPES, MEDIA_TYPES


class User(models.Model):
    telegram_id = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    name = models.CharField(max_length=100, null=True)
    age = models.IntegerField(null=True)
    bio = models.TextField(null=True)
    lat = models.CharField(max_length=100, null=True)
    long = models.CharField(max_length=100, null=True)
    gender = models.CharField(max_length=1, db_index=True, choices=GENDER_TYPES, null=True)
    search_gender = models.CharField(max_length=1, db_index=True, choices=GENDER_TYPES, null=True)

    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserMedia(models.Model):
    user = models.ForeignKey(User, related_name='images', on_delete=models.SET_NULL, null=True)
    media_id = models.CharField(max_length=256)
    media_type = models.CharField(max_length=1, choices=MEDIA_TYPES)


class Action(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions_performed')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_actions')
    action_type = models.IntegerField(choices=ACTION_TYPES)
    is_matched = models.BooleanField(default=False)
    text = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Report(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    to_user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='complaints', null=True)
    text = models.TextField()
    image_id = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    text = models.TextField()
    image = models.ImageField()
    to_user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='notifications', null=True)
    to_all = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
