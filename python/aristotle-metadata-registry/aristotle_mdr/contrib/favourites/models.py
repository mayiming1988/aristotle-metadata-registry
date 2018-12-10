from django.db import models
from aristotle_mdr.models import _concept, PossumProfile


class Tag(models.Model):

    class Meta:
        unique_together = ('profile', 'name')

    profile = models.ForeignKey(
        PossumProfile,
        related_name='tags'
    )
    name = models.CharField(
        max_length=200,
        blank=True
    )
    description = models.TextField(
        blank=True
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    primary = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.name

    def can_view(self, user):
        return user.profile == self.profile

    def can_edit(self, user):
        return self.can_view(user)


class Favourite(models.Model):

    class Meta:
        unique_together = ('tag', 'item')

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
