from reversion.models import Version
from aristotle_mdr import messages
from aristotle_mdr.contrib.async_signals.utils import safe_object
from django.contrib.auth import get_user_model

import logging
logger = logging.getLogger(__name__)


def item_saved(message, **kwargs):

    user_email = get_user_model().objects.get(pk=message.get('user_id')).email

    version = safe_object(message)
    instance = version.object

    if Version.objects.get_for_object(instance).count() < 2:
        created = True
    else:
        created = False

    for user in instance.favourited_by:
        if user_email and user.email is not user_email:
            messages.favourite_updated(recipient=user, obj=instance)

    for user in instance.editable_by:
        if not created:
            if user_email and user.email is not user_email:
                messages.items_i_can_edit_updated(recipient=user, obj=instance)

    if instance.workgroup:
        for user in instance.workgroup.users_for_role('viewer'):
            if user_email and user.email is not user_email:
                if created:
                    messages.workgroup_item_new(recipient=user, obj=instance)
                else:
                    messages.workgroup_item_updated(recipient=user, obj=instance)


def new_comment_created(message, **kwargs):
    comment = safe_object(message)
    post = comment.post
    messages.new_comment_created(recipient=post.author, comment=comment)


def new_post_created(message, **kwargs):
    post = safe_object(message)

    for user in post.workgroup.member_list:
        if user != post.author:
            messages.new_post_created(recipient=user, post=post)


def status_changed(message, **kwargs):
    new_status = safe_object(message)
    concept = new_status.concept
    seen_registrars = set()
    for status in concept.current_statuses().all():
        for registrar in status.registrationAuthority.registrars.all():
            if registrar not in seen_registrars:
                if concept.statuses.filter(registrationAuthority=new_status.registrationAuthority).count() <= 1:
                    # 0 or 1 because the transaction may not be complete yet
                    messages.registrar_item_registered(recipient=registrar, obj=concept, ra=new_status.registrationAuthority, status=str(new_status.state_name))
                else:
                    messages.registrar_item_changed_status(recipient=registrar, obj=concept, ra=new_status.registrationAuthority, status=str(new_status.state_name))
                seen_registrars.add(registrar)


def item_superseded(message, **kwargs):
    new_super_rel = safe_object(message)
    concept = new_super_rel.older_item

    for user in concept.favourited_by.all():
        if concept.can_view(user) and new_super_rel.newer_item.can_view(user):
            messages.favourite_superseded(recipient=user, obj=concept)

    for user in concept.editable_by:
        if concept.can_view(user) and new_super_rel.newer_item.can_view(user):
            messages.items_i_can_edit_superseded(recipient=user, obj=concept)

    if concept.workgroup:
        for user in concept.workgroup.users_for_role('viewer'):
            if concept.can_view(user) and new_super_rel.newer_item.can_view(user):
                messages.workgroup_item_superseded(recipient=user, obj=concept)

    for status in concept.current_statuses().all():
        for registrar in status.registrationAuthority.registrars.all():
            if concept.can_view(registrar) and new_super_rel.newer_item.can_view(registrar):
                messages.registrar_item_superseded(recipient=registrar, obj=concept, ra=status.registrationAuthority)


def issue_created(issue, **kwargs):
    safe_issue = safe_object(issue)
    if safe_issue.item.workgroup:
        for user in safe_issue.item.workgroup.member_list:
            if user != safe_issue.submitter:
                messages.issue_created_workgroup(recipient=user, obj=safe_issue)

    for user in safe_issue.item.favourited_by:
        if user != safe_issue.submitter:
            messages.issue_created_favourite(recipient=user, obj=safe_issue)

    for user in safe_issue.item.editable_by:
        if user != safe_issue.submitter:
            messages.issue_created_items_i_can_edit(recipient=user, obj=safe_issue)


def issue_commented(issue_comment, **kwargs):
    safe_issue_comment = safe_object(issue_comment)
    if safe_issue_comment.issue.item.workgroup:
        for user in safe_issue_comment.issue.item.workgroup.member_list:
            if user != safe_issue_comment.author:
                messages.issue_comment_created_workgroup(recipient=user, obj=safe_issue_comment)

    for user in safe_issue_comment.issue.item.favourited_by:
        if user != safe_issue_comment.author:
            messages.issue_comment_created_favourite(recipient=user, obj=safe_issue_comment)

    for user in safe_issue_comment.issue.item.editable_by:
        if user != safe_issue_comment.author:
            messages.issue_comment_created_items_i_can_edit(recipient=user, obj=safe_issue_comment)
