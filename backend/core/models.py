from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

from model_utils.fields import AutoCreatedField, AutoLastModifiedField


VOTE_TYPES = Choices(
        ("UP_VOTE", "UP_VOTE"),
        ("DOWN_VOTE", "DOWN_VOTE")
    )


class BaseAppModel(models.Model):
    created_date = models.DateField(blank=True, null=True, auto_now_add=True)
    updated_date = models.DateField(blank=True, null=True)
    status = models.BooleanField(blank=True, null=True, default=False)

    class Meta:
        abstract = True


class IndexedTimeStampedModel(models.Model):
    created = AutoCreatedField(_("created"), db_index=True)
    modified = AutoLastModifiedField(_("modified"), db_index=True)

    class Meta:
        abstract = True


class BaseVoteModel(BaseAppModel):
    vote_type = models.CharField(
        choices=VOTE_TYPES,
        null=False,
        blank=False,
        max_length=9
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, blank=True, null=False)

    class Meta:
        abstract = True
