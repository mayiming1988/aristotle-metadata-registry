from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, post_delete, pre_save
from django.core.exceptions import FieldDoesNotExist
from django.dispatch import receiver

from model_utils.models import TimeStampedModel
from aristotle_mdr.fields import ConceptForeignKey
from aristotle_mdr.models import _concept
from aristotle_mdr.utils import (url_slugify_issue)
from aristotle_mdr.contrib.async_signals.utils import fire
from ckeditor_uploader.fields import RichTextUploadingField as RichTextField
from jsonfield import JSONField

import logging
logger = logging.getLogger(__name__)


class Issue(TimeStampedModel):

    # Fields on a concept that are proposable (must be text)
    proposable_fields = ['name', 'definition', 'references', 'origin', 'comments']

    name = models.CharField(max_length=1000)
    description = models.TextField(blank=True)
    item = ConceptForeignKey(
        _concept,
        related_name='issues'
    )
    submitter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='issues'
    )
    isopen = models.BooleanField(default=True)
    proposal_field = models.TextField(blank=True)
    proposal_value = models.TextField(blank=True)

    def can_edit(self, user):
        return user.id == self.submitter.id

    def can_view(self, user):
        return self.item.can_view(user)

    def can_alter_open(self, user):
        return self.can_edit(user) or self.item.can_edit(user)

    def get_absolute_url(self):
        return url_slugify_issue(self)

    @classmethod
    def get_propose_fields(cls):
        """
        Return list of field names and whether fields are html
        for proposable fields
        """
        fields = []

        for fname in cls.proposable_fields:
            try:
                field = _concept._meta.get_field(fname)
            except FieldDoesNotExist:
                field = None

            if field:
                html = False
                if issubclass(type(field), RichTextField):
                    html = True

                fields.append({
                    'name': fname,
                    'html': html
                })
        return fields

    def __str__(self):
        return self.name


class IssueComment(TimeStampedModel):

    issue = models.ForeignKey(Issue,
                              related_name='comments'
                              )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='issue_comments'
    )
    body = models.TextField()

    def can_view(self, user):
        return self.issue.item.can_view(user)

    def can_edit(self, user):
        return user.id == self.author.id


@receiver(post_save, sender=Issue)
def new_issue_created(sender, instance, *args, **kwargs):
    # issue = kwargs['instance']
    if kwargs.get('created'):
        fire("concept_changes.issue_created", obj=instance, **kwargs)


@receiver(post_save, sender=IssueComment)
def new_issue_comment_created(sender, instance, *args, **kwargs):
    # issue_comment = kwargs['instance']
    if kwargs.get('created'):
        fire("concept_changes.issue_commented", obj=instance, **kwargs)
