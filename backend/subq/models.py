from django.conf import settings
from django.db import models


# Create your models here.
from django.utils.text import slugify

from core.models import BaseAppModel


class SubQ(BaseAppModel):
    sub_name = models.CharField(unique=True, max_length=250, db_index=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=80, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, blank=True, null=True, related_name="owned_subs")

    class Meta:
        db_table = 'subq'
        verbose_name = "Sub Q"

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.slug:
            self.slug = slugify(self.sub_name)


class SubQFollower(BaseAppModel):
    is_moderator = models.BooleanField(default=False, blank=True, null=True)
    join_date = models.DateField(blank=True, null=True)
    notifications_enabled = models.BooleanField(default=True, blank=True)
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, blank=True, null=True, related_name="subs")
    subq = models.ForeignKey(SubQ, models.DO_NOTHING, blank=True, null=True, related_name="followers")
    is_banned = models.BooleanField(blank=True, null=True, default=False)

    class Meta:
        db_table = 'subq_follower'
        verbose_name = "Sub Follower"
