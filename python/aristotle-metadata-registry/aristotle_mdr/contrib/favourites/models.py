from django.db import models
from aristotle_mdr.models import _concept, PossumProfile


class Tag(models.Model):

    profile = models.ForeignKey(
        PossumProfile,
        related_name='tags'
    )
    name = models.CharField(
        max_length=200,
        blank=True
    )
    description = models.TextField()
    created = models.DateTimeField(
        auto_now_add=True
    )
    primary = models.BooleanField(
        default=False
    )

    def __str__(self):
        if self.primary:
            return ' - '.join([self.profile.user.email, 'Primary'])
        else:
            return ' - '.join([self.profile.user.email, self.name])


class Favourite(models.Model):

    tag = models.ForeignKey(
        Tag,
        related_name='favourites'
    )
    item = models.ForeignKey(
        _concept,
        related_name='favourites'
    )
    created = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return ' - '.join([self.tag.name, self.item.name])
