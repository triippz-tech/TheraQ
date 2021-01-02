from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models


# Create your models here.
from django.utils.text import slugify

from core.models import BaseAppModel


User = get_user_model()


class SubQ(BaseAppModel):
    sub_name = models.CharField(unique=True, max_length=250, db_index=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=80, unique=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, blank=True, null=True, related_name="owned_subs")

    class Meta:
        db_table = 'subq'
        verbose_name = "Sub Q"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.sub_name)
        return super(SubQ, self).save(*args, **kwargs)

    def archive(self):
        self.status = True
        self.save()


class SubQFollower(BaseAppModel):
    is_moderator = models.BooleanField(default=False, blank=True, null=True)
    join_date = models.DateField(blank=True, null=True, auto_now_add=True)
    notifications_enabled = models.BooleanField(default=True, blank=True)
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, blank=True, null=True, related_name="subs")
    subq = models.ForeignKey(SubQ, models.DO_NOTHING, blank=True, null=True, related_name="followers")
    is_banned = models.BooleanField(blank=True, null=True, default=False)
    ban_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'subq_follower'
        verbose_name = "Sub Follower"

    def archive(self):
        self.status = True
        self.save()

    def ban(self):
        self.is_banned = True
        self.status = True
        self.ban_date = datetime.now()
        self.save()

    @staticmethod
    def join_sub(user: User, subq: SubQ):
        subq_follower = SubQFollower(follower=user, subq=subq)
        subq_follower.save()
        return subq_follower
