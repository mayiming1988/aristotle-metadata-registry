from notifications.signals import notify
from aristotle_bg_workers.tasks import send_notification_email
from django.utils.translation import ugettext as _


def workgroup_item_updated(recipient, obj):
    if check_within_aristotle_notification_permission(recipient) and \
            recipient.profile.notificationPermissions["metadata changes"]["general changes"]["items in my workgroups"]:
        notify.send(obj, recipient=recipient, verb=_("has been updated in the workgroup"), target=obj.workgroup)

    message = obj.name + _(" was modified in the workgroup ") + obj.workgroup.name
    send_email(recipient, message)


def favourite_updated(recipient, obj):
    if check_within_aristotle_notification_permission(recipient) and \
            recipient.profile.notificationPermissions["metadata changes"]["general changes"]["items I have tagged / favourited"]:
        if obj.workgroup is not None:
            notify.send(
                obj,
                recipient=recipient,
                verb=_("(favourite item) has been updated in the workgroup"),
                target=obj.workgroup
            )
        else:
            notify.send(obj, recipient=recipient, verb=_("(favourite item) has been updated."))

    message = _("A favourited item has been changed: ") + obj.name
    send_email(recipient, message)


def items_i_can_edit_updated(recipient, obj):
    if check_within_aristotle_notification_permission(recipient) and \
            recipient.profile.notificationPermissions["metadata changes"]["general changes"]["any items I can edit"]:
        if obj.workgroup is not None:
            notify.send(
                obj,
                recipient=recipient,
                verb=_("(editable item) has been updated in the workgroup"),
                target=obj.workgroup
            )
        else:
            notify.send(obj, recipient=recipient, verb=_("(editable item) has been updated."))

    message = _("An item you can edit has been changed: ") + obj.name
    send_email(recipient, message)


def workgroup_item_superseded(recipient, obj):
    if check_within_aristotle_notification_permission(recipient) and \
            recipient.profile.notificationPermissions["metadata changes"]["superseded"]["items in my workgroups"]:
        notify.send(obj, recipient=recipient, verb=_("has been superseded in the workgroup"), target=obj.workgroup)

    message = obj.name + _(" was superseded in the workgroup ") + obj.workgroup.name
    send_email(recipient, message)


def favourite_superseded(recipient, obj):
    if check_within_aristotle_notification_permission(recipient) and \
            recipient.profile.notificationPermissions["metadata changes"]["superseded"]["items I have tagged / favourited"]:
        if obj.workgroup is not None:
            notify.send(
                obj,
                recipient=recipient,
                verb=_("(favourite item) has been superseded in the workgroup"),
                target=obj.workgroup
            )
        else:
            notify.send(obj, recipient=recipient, verb=_("(favourite item) has been superseded."))

    message = _("A favourited item has been superseded: ") + obj.name
    send_email(recipient, message)


def items_i_can_edit_superseded(recipient, obj):
    if check_within_aristotle_notification_permission(recipient) and \
            recipient.profile.notificationPermissions["metadata changes"]["superseded"]["any items I can edit"]:
        if obj.workgroup is not None:
            notify.send(
                obj,
                recipient=recipient,
                verb=_("(editable item) has been superseded in the workgroup"),
                target=obj.workgroup
            )
        else:
            notify.send(obj, recipient=recipient, verb=_("(editable item) has been superseded."))

    message = _("An item you can edit has been superseded: ") + obj.name
    send_email(recipient, message)


def workgroup_item_new(recipient, obj):
    if check_within_aristotle_notification_permission(recipient) and \
            recipient.profile.notificationPermissions["metadata changes"]["new items"]["new items in my workgroups"]:
        notify.send(obj, recipient=recipient, verb=_("has been created in the workgroup"), target=obj.workgroup)

    message = obj.name + _(" was created in the workgroup ") + obj.workgroup.name
    send_email(recipient, message)


def registrar_item_superseded(recipient, obj, ra):
    if check_within_aristotle_notification_permission(recipient) and \
            recipient.profile.notificationPermissions['registrar']['item superseded']:
        notify.send(obj, recipient=recipient, verb=_("(item registered by ") + ra.name + _(") has been superseded."))

    message = _("An item registered by your registration authority has been superseded: ") + obj.name
    send_email(recipient, message)


def registrar_item_registered(recipient, obj, ra, status):
    if check_within_aristotle_notification_permission(recipient) and \
            recipient.profile.notificationPermissions['registrar']['item registered']:
        notify.send(
            obj,
            recipient=recipient,
            verb=_("has been registered by ") + ra.name + _(" with the status '") + status + _("'.")
        )

    message = _("An item has been registered by your registration authority: ") + obj.name
    send_email(recipient, message)


def registrar_item_changed_status(recipient, obj, ra, status):
    if check_within_aristotle_notification_permission(recipient) and \
            recipient.profile.notificationPermissions['registrar']['item changed status']:
        notify.send(
            obj,
            recipient=recipient,
            verb=_("(item registered by ") + ra.name + _(") has changed its status to '") + status + _("'.")
        )

    message = _("An item registered by your registration authority has changed status: ") + obj.name
    send_email(recipient, message)


def review_request_created(recipient, obj):
    if check_within_aristotle_notification_permission(recipient) and \
            recipient.profile.notificationPermissions['registrar']['review request created']:
        notify.send(
            obj,
            recipient=recipient,
            verb=obj.requester.full_name + _(" created a review request: ") + obj.title_short
        )

    message = obj.requester.full_name + _(" created a review request: ") + obj.title_short

    send_email(recipient, message)


def review_request_updated(recipient, obj):
    if check_within_aristotle_notification_permission(recipient) and \
            recipient.profile.notificationPermissions['registrar']['review request updated']:
        notify.send(
            obj,
            recipient=recipient,
            verb=_("Review request updated: ") + obj.title_short
        )

    message = _("Review request updated: ") + obj.title_short
    send_email(recipient, message)


def issue_created_workgroup(recipient, obj):
    if check_within_aristotle_notification_permission(recipient) and \
            recipient.profile.notificationPermissions['issues']['items in my workgroups']:
        notify.send(obj, recipient=recipient, verb=_("(issue) has been created on the item"), target=obj.item)

    message = _("A new issue was created on the item ") + obj.item.name
    send_email(recipient, message)


def issue_comment_created_workgroup(recipient, obj):
    if check_within_aristotle_notification_permission(recipient) and \
            recipient.profile.notificationPermissions['issues']['items in my workgroups']:
        notify.send(
            obj.issue,
            recipient=recipient,
            verb=_("A new comment on an Issue has been created in the workgroup:"),
            target=obj.issue.item.workgroup
        )

    message = _("A new comment on an issue has been created.")
    send_email(recipient, message)


def issue_created_favourite(recipient, obj):
    if check_within_aristotle_notification_permission(recipient) and \
            recipient.profile.notificationPermissions['issues']['items I have tagged / favourited']:
        notify.send(obj, recipient=recipient, verb=_("(issue) has been created on a favourite item:"), target=obj.item)

    message = _("An issue has been created on a favourite item.")
    send_email(recipient, message)


def issue_comment_created_favourite(recipient, obj):
    if check_within_aristotle_notification_permission(recipient) and \
            recipient.profile.notificationPermissions['issues']['items I have tagged / favourited']:
        notify.send(
            obj.issue,
            recipient=recipient,
            verb=_("A new comment has been created on an issue of a favourite item:"),
            target=obj.issue.item
        )

    message = _("A new comment has been created for an issue of a favourite item.")
    send_email(recipient, message)


def issue_created_items_i_can_edit(recipient, obj):
    if check_within_aristotle_notification_permission(recipient) and \
            recipient.profile.notificationPermissions['issues']['any items I can edit']:
        notify.send(
            obj,
            recipient=recipient,
            verb=_("(issue) has been created on an item you can edit:"),
            target=obj.item
        )

    message = _("A new issue has been created on an item you can edit.")
    send_email(recipient, message)


def issue_comment_created_items_i_can_edit(recipient, obj):
    if check_within_aristotle_notification_permission(recipient) and \
            recipient.profile.notificationPermissions['issues']['any items I can edit']:
        notify.send(
            obj.issue,
            recipient=recipient,
            verb=_("A new comment has been created on an issue of an item you can edit:"),
            target=obj.issue.item
        )

    message = _("A new comment has been created for an issue you can edit.")
    send_email(recipient, message)


def new_post_created(recipient, post):
    if check_within_aristotle_notification_permission(recipient) and \
            recipient.profile.notificationPermissions['discussions']['new posts']:
        if post.author:
            if post.workgroup:
                notify.send(
                    post,
                    recipient=recipient,
                    verb=_("(discussion) has been created in the workgroup:"),
                    target=post.workgroup
                )
            else:
                notify.send(
                    post,
                    recipient=recipient,
                    verb=_("(discussion) has been created.")
                )

    if post.author and post.workgroup:
        message = post.author.display_name + _(" made a new post in the workgroup {}.").format(post.workgroup)
    elif post.author:
        message = post.author.display_name + _(" made a new post.")
    elif post.workgroup:
        message = _("A new post was created in the workgroup {}").format(post.workgroup)
    else:
        message = _("A new post was created.")
    send_email(recipient, message)


def new_comment_created(recipient, comment):
    if check_within_aristotle_notification_permission(recipient) and \
            recipient.profile.notificationPermissions['discussions']['new comments']:
        if comment.author:
            notify.send(
                comment,
                recipient=recipient,
                verb=_("(comment) has been created in the discussion:"),
                target=comment.post
            )

    message = comment.author.display_name + _(" commented on your post ") + comment.post.title
    send_email(recipient, message)


def send_email(recipient, message):
    """
    The purpose of this function is to send an email to the recipient
    only if the 'email' checkbox is selected in the Notification Permissions
    of the recipient argument.
    :param recipient: User object who we are going to check the notification permission.
    :param message: String message content of the email to be sent.
    """
    if recipient.profile.notificationPermissions["notification methods"]["email"]:
        send_notification_email.delay(recipient.email, message)


def check_within_aristotle_notification_permission(recipient):
    """
    The purpose of this function is to check if the 'within aristotle' checkbox
    has been selected in Notification Permissions of the recipient argument.
    :param recipient: User object who we are going to check the notification permission.
    :return: True if the checkbox is selected. NoneType otherwise.
    """
    if recipient.profile.notificationPermissions["notification methods"]["within aristotle"]:
        return True
