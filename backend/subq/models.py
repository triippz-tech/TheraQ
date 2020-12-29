from django.conf import settings
from django.db import models


# Create your models here.
from django.utils.text import slugify

from core.models import BaseAppModel


class SubQ(BaseAppModel):
    sub_name = models.CharField(unique=True, max_length=250, db_index=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=80, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'subq'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.slug:
            self.slug = slugify(self.sub_name)


class SubQFollower(BaseAppModel):
    is_moderator = models.BooleanField(default=False, blank=True, null=True)
    join_date = models.DateField(blank=True, null=True)
    notifications_enabled = models.BooleanField(default=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, blank=True, null=True)
    subq = models.ForeignKey(SubQ, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'subq_follower'
