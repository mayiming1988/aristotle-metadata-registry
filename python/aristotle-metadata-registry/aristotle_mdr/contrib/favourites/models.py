from django.db import models
from aristotle_mdr import models as mdr_models


class Tag(models.Model):

    profile = models.ForeignKey(
        mdr_models.PossumProfile,
        related_name='favourites'
    )
    name = models.CharField(
        max_length=200,
        blank=True
    )
    description = models.TextField()
    created = models.DateTimeField(
        auto_now_add=True
    )


class Favourite(models.Model):

    tag = models.ForeignKey(
        Tag,
        related_name='favourites'
    )
    item = models.ForeignKey(
        mdr_models._concept,
        related_name='favourites'
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
