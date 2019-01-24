from notifications.signals import notify
from aristotle_bg_workers.tasks import send_notification_email
from functools import wraps
import logging
logger = logging.getLogger(__name__)


def notif_accepted_email(func):
    """Check if the 'email' checkbox has been selected in Notification Permissions for this user."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs['recipient'].profile.notificationPermissions["notification methods"]["email"]:
            message = ""
            if func.__name__ == "workgroup_item_updated":
                message = kwargs['obj'].name + " was modified in the workgroup " + kwargs['obj'].workgroup.name
            elif func.__name__ == "favourite_updated":
                message = "A favourited item has been changed: " + kwargs['obj'].name
            elif func.__name__ == "items_i_can_edit_updated":
                message = "An item you can edit has been changed: " + kwargs['obj'].name
            elif func.__name__ == "workgroup_item_superseded":
                message = kwargs['obj'].name + " was superseded in the workgroup " + kwargs['obj'].workgroup.name
            elif func.__name__ == "favourite_superseded":
                message = "A favourited item has been superseded: " + kwargs['obj'].name
            elif func.__name__ == "items_i_can_edit_superseded":
                message = "An item you can edit has been superseded: " + kwargs['obj'].name
            elif func.__name__ == "registrar_item_superseded":
                message = "An item registered by your registration authority has been superseded: " + kwargs['obj'].name
            elif func.__name__ == "registrar_item_registered":
                message = "An item has been registered by your registration authority: " + kwargs['obj'].name
            elif func.__name__ == "registrar_item_changed_status":
                message = "An item registered by your registration authority has changed status: " + kwargs['obj'].name
            elif func.__name__ == "workgroup_item_new":
                message = kwargs['obj'] + " was created in the workgroup " + kwargs['obj'].workgroup.name
            elif func.__name__ == "new_comment_created":
                message = kwargs['comment'].author + " commented on your post " + kwargs['comment'].post
            elif func.__name__ == "new_post_created":
                message = kwargs['post'].author + " made a new post"
            elif func.__name__ == "review_request_created":
                message = kwargs['requester'].full_name + " requested concept review"
            elif func.__name__ == "review_request_updated":
                message = "concept was reviewed by " + kwargs['reviewer'].full_name
            send_notification_email.delay(kwargs['recipient'].email, message)
        return func(*args, **kwargs)
    return wrapper


def notif_accepted_within_aristotle(func):
    """Check if the 'within aristotle' checkbox has been selected in Notification Permissions for this user."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs['recipient'].profile.notificationPermissions["notification methods"]["within aristotle"]:
            return func(*args, **kwargs)
    return wrapper


def notif_general_changes_workgroups(func):
    """Check if the 'items in my workgroups' checkbox under 'general changes' has been selected in
    Notification Permissions for this user."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs['recipient'].profile.notificationPermissions["metadata changes"]["general changes"]["items in my workgroups"]:
            return func(*args, **kwargs)
    return wrapper


def notif_general_changes_favourited(func):
    """Check if the 'items I have tagged / favourited' checkbox under 'general changes' has been selected in
    Notification Permissions for this user."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs['recipient'].profile.notificationPermissions["metadata changes"]["general changes"]["items I have tagged / favourited"]:
            return func(*args, **kwargs)
    return wrapper


def notif_general_changes_items_i_can_edit(func):
    """Check if the 'any items I can edit' checkbox under 'general changes' has been selected in
    Notification Permissions for this user."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs['recipient'].profile.notificationPermissions["metadata changes"]["general changes"]["any items I can edit"]:
            return func(*args, **kwargs)
    return wrapper


def notif_superseded_workgroups(func):
    """Check if the 'items in my workgroups' checkbox under 'superseded' has been selected in
    Notification Permissions for this user."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs['recipient'].profile.notificationPermissions["metadata changes"]["superseded"]["items in my workgroups"]:
            return func(*args, **kwargs)
    return wrapper


def notif_superseded_favourited(func):
    """Check if the 'items I have tagged / favourited' checkbox under 'superseded' has been selected in
    Notification Permissions for this user."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs['recipient'].profile.notificationPermissions["metadata changes"]["superseded"]["items I have tagged / favourited"]:
            return func(*args, **kwargs)
    return wrapper


def notif_superseded_i_can_edit(func):
    """Check if the 'any items I can edit' checkbox under 'superseded' has been selected in
    Notification Permissions for this user."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs['recipient'].profile.notificationPermissions["metadata changes"]["superseded"]["any items I can edit"]:
            return func(*args, **kwargs)
    return wrapper


@notif_general_changes_workgroups
@notif_accepted_email
@notif_accepted_within_aristotle
def workgroup_item_updated(recipient, obj):
    notify.send(obj, recipient=recipient, verb="was modified in the workgroup", target=obj.workgroup)


@notif_general_changes_favourited
@notif_accepted_email
@notif_accepted_within_aristotle
def favourite_updated(recipient, obj):
    notify.send(obj, recipient=recipient, verb="A favourited item has been changed:", target=obj)


@notif_general_changes_items_i_can_edit
@notif_accepted_email
@notif_accepted_within_aristotle
def items_i_can_edit_updated(recipient, obj):
    notify.send(obj, recipient=recipient, verb="An item you can edit has been changed:", target=obj)


@notif_superseded_workgroups
@notif_accepted_email
@notif_accepted_within_aristotle
def workgroup_item_superseded(recipient, obj):
    notify.send(obj, recipient=recipient, verb="was superseded in the workgroup", target=obj.workgroup)


@notif_superseded_favourited
@notif_accepted_email
@notif_accepted_within_aristotle
def favourite_superseded(recipient, obj):
    notify.send(obj, recipient=recipient, verb="A favourited item has been superseded:", target=obj)


@notif_superseded_i_can_edit
@notif_accepted_email
@notif_accepted_within_aristotle
def items_i_can_edit_superseded(recipient, obj):
    notify.send(obj, recipient=recipient, verb="An item you can edit has been superseded:", target=obj)


@notif_accepted_email
@notif_accepted_within_aristotle
def registrar_item_superseded(recipient, obj):
    notify.send(obj, recipient=recipient, verb="An item registered by your registration authority has been superseded:", target=obj)


@notif_accepted_email
@notif_accepted_within_aristotle
def registrar_item_registered(recipient, obj):
    notify.send(obj, recipient=recipient, verb="An item has been registered by your registration authority:", target=obj)


@notif_accepted_email
@notif_accepted_within_aristotle
def registrar_item_changed_status(recipient, obj):
    notify.send(obj, recipient=recipient, verb="An item registered by your registration authority has changed status:", target=obj)


@notif_accepted_email
@notif_accepted_within_aristotle
def workgroup_item_new(recipient, obj):
    notify.send(obj, recipient=recipient, verb="was created in the workgroup", target=obj.workgroup)


@notif_accepted_email
@notif_accepted_within_aristotle
def new_comment_created(recipient, comment):
    if comment.author:
        notify.send(comment.author, recipient=recipient, verb="commented on your post", target=comment.post)


@notif_accepted_email
@notif_accepted_within_aristotle
def new_post_created(recipient, post):
    if post.author:
        notify.send(post.author, recipient=recipient, verb="made a new post", target=post, action_object=post.workgroup)


@notif_accepted_email
@notif_accepted_within_aristotle
def review_request_created(recipient, review_request, requester):
    notify.send(requester, recipient=recipient, verb="requested concept review", target=review_request)


@notif_accepted_email
@notif_accepted_within_aristotle
def review_request_updated(recipient, review_request, reviewer):
    if reviewer:
        notify.send(reviewer, recipient=recipient, verb="concept was reviewed", target=review_request)
    else:
        # Maybe it was auto reviewed, or updated manually?
        notify.send(review_request, recipient=recipient, verb="concept was reviewed", target=review_request)
