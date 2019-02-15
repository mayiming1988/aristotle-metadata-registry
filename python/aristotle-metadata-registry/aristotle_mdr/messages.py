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
            elif func.__name__ == "workgroup_item_new":
                message = kwargs['obj'].name + " was created in the workgroup " + kwargs['obj'].workgroup.name
            elif func.__name__ == "registrar_item_superseded":
                message = "An item registered by your registration authority has been superseded: " + kwargs['obj'].name
            elif func.__name__ == "registrar_item_registered":
                message = "An item has been registered by your registration authority: " + kwargs['obj'].name
            elif func.__name__ == "registrar_item_changed_status":
                message = "An item registered by your registration authority has changed status: " + kwargs['obj'].name
            elif func.__name__ == "review_request_created":
                message = kwargs['requester'].full_name + " requested concept review"
            elif func.__name__ == "review_request_updated":
                message = "concept was reviewed by " + kwargs['reviewer'].full_name
            elif func.__name__ == "issue_created_workgroup":
                message = "A new issue was created on the item " + kwargs['obj'].item.name
            elif func.__name__ == "issue_comment_created_workgroup":
                message = "A new comment on an issue has been created"
            elif func.__name__ == "issue_created_favourite":
                message = "An issue has been created on a favourite item"
            elif func.__name__ == "issue_comment_created_favourite":
                message = "A new comment has been created for an issue of a favourite item."
            elif func.__name__ == "issue_created_items_i_can_edit":
                message = "A new issue has been created on an item you can edit."
            elif func.__name__ == "issue_comment_created_items_i_can_edit":
                message = "A new comment has been created for an issue you can edit"
            elif func.__name__ == "new_post_created":
                message = kwargs['post'].author + " made a new post"
            elif func.__name__ == "new_comment_created":
                message = kwargs['comment'].author + " commented on your post " + kwargs['comment'].post
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


def notif_new_items_in_my_workgroups(func):
    """Check if the 'new items in my workgroups' checkbox under 'new items' has been selected in
    Notification Permissions for this user."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs['recipient'].profile.notificationPermissions["metadata changes"]["new items"]["new items in my workgroups"]:
            return func(*args, **kwargs)
    return wrapper


def notif_registrar_item_superseded(func):
    """Check if the 'item superseded' checkbox under 'registrar' has been selected in
        Notification Permissions for this user."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs['recipient'].profile.notificationPermissions['registrar']['item superseded']:
            return func(*args, **kwargs)
    return wrapper


def notif_registrar_item_registered(func):
    """Check if the 'item registered' checkbox under 'registrar' has been selected in
        Notification Permissions for this user."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs['recipient'].profile.notificationPermissions['registrar']['item registered']:
            return func(*args, **kwargs)
    return wrapper


def notif_registrar_item_changed_status(func):
    """Check if the 'item changed status' checkbox under 'registrar' has been selected in
        Notification Permissions for this user."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs['recipient'].profile.notificationPermissions['registrar']['item changed status']:
            return func(*args, **kwargs)
    return wrapper


def notif_registrar_review_request_created(func):
    """Check if the 'review request created' checkbox under 'registrar' has been selected in
        Notification Permissions for this user."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs['recipient'].profile.notificationPermissions['registrar']['review request created']:
            return func(*args, **kwargs)
    return wrapper


def notif_registrar_review_request_updated(func):
    """Check if the 'review request updated' checkbox under 'registrar' has been selected in
        Notification Permissions for this user."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs['recipient'].profile.notificationPermissions['registrar']['review request updated']:
            return func(*args, **kwargs)
    return wrapper


def notif_issues_items_in_my_workgroups(func):
    """Check if the 'items in my workgroups' checkbox under 'issues' has been selected in
        Notification Permissions for this user."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs['recipient'].profile.notificationPermissions['issues']['items in my workgroups']:
            return func(*args, **kwargs)
    return wrapper


def notif_issues_favourited(func):
    """Check if the 'items I have tagged / favourited' checkbox under 'issues' has been selected in
        Notification Permissions for this user."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs['recipient'].profile.notificationPermissions['issues']['items I have tagged / favourited']:
            return func(*args, **kwargs)
    return wrapper


def notif_issues_i_can_edit(func):
    """Check if the 'any items I can edit' checkbox under 'issues' has been selected in
        Notification Permissions for this user."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs['recipient'].profile.notificationPermissions['issues']['any items I can edit']:
            return func(*args, **kwargs)
    return wrapper


def notif_discussions_new_posts(func):
    """Check if the 'new posts' checkbox under 'discussions' has been selected in
        Notification Permissions for this user."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs['recipient'].profile.notificationPermissions['discussions']['new posts']:
            return func(*args, **kwargs)
    return wrapper


def notif_discussions_new_comments(func):
    """Check if the 'new comments' checkbox under 'discussions' has been selected in
        Notification Permissions for this user."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs['recipient'].profile.notificationPermissions['discussions']['new comments']:
            return func(*args, **kwargs)
    return wrapper


@notif_general_changes_workgroups
@notif_accepted_email
@notif_accepted_within_aristotle
def workgroup_item_updated(recipient, obj):
    notify.send(obj, recipient=recipient, verb="has been updated in the workgroup", target=obj.workgroup)


@notif_general_changes_favourited
@notif_accepted_email
@notif_accepted_within_aristotle
def favourite_updated(recipient, obj):
    if obj.workgroup is not None:
        notify.send(obj, recipient=recipient, verb="(favourite item) has been updated in the workgroup", target=obj.workgroup)
    else:
        notify.send(obj, recipient=recipient, verb="(favourite item) has been updated.")


@notif_general_changes_items_i_can_edit
@notif_accepted_email
@notif_accepted_within_aristotle
def items_i_can_edit_updated(recipient, obj):
    if obj.workgroup is not None:
        notify.send(obj, recipient=recipient, verb="(editable item) has been updated in the workgroup", target=obj.workgroup)
    else:
        notify.send(obj, recipient=recipient, verb="(editable item) has been updated.")


@notif_superseded_workgroups
@notif_accepted_email
@notif_accepted_within_aristotle
def workgroup_item_superseded(recipient, obj):
    notify.send(obj, recipient=recipient, verb="has been superseded in the workgroup", target=obj.workgroup)


@notif_superseded_favourited
@notif_accepted_email
@notif_accepted_within_aristotle
def favourite_superseded(recipient, obj):
    if obj.workgroup is not None:
        notify.send(obj, recipient=recipient, verb="(favourite item) has been superseded in the workgroup", target=obj.workgroup)
    else:
        notify.send(obj, recipient=recipient, verb="(favourite item) has been superseded.")


@notif_superseded_i_can_edit
@notif_accepted_email
@notif_accepted_within_aristotle
def items_i_can_edit_superseded(recipient, obj):
    if obj.workgroup is not None:
        notify.send(obj, recipient=recipient, verb="(editable item) has been superseded in the workgroup",
                    target=obj.workgroup)
    else:
        notify.send(obj, recipient=recipient, verb="(editable item) has been superseded.")


@notif_new_items_in_my_workgroups
@notif_accepted_email
@notif_accepted_within_aristotle
def workgroup_item_new(recipient, obj):
    notify.send(obj, recipient=recipient, verb="has been created in the workgroup", target=obj.workgroup)


@notif_registrar_item_superseded
@notif_accepted_email
@notif_accepted_within_aristotle
def registrar_item_superseded(recipient, obj, ra):
    notify.send(obj, recipient=recipient, verb="(item registered by " + ra.name + ") has been superseded.")


@notif_registrar_item_registered
@notif_accepted_email
@notif_accepted_within_aristotle
def registrar_item_registered(recipient, obj, ra, status):
    notify.send(obj, recipient=recipient, verb="has been registered by " + ra.name + " with the status '" + status + "'.")


@notif_registrar_item_changed_status
@notif_accepted_email
@notif_accepted_within_aristotle
def registrar_item_changed_status(recipient, obj, ra, status):
    logger.critical("THIS IS THE STATUS:")
    logger.critical(status)
    notify.send(obj, recipient=recipient, verb="(item registered by " + ra.name + ") has changed its status to '" + status + "'.")


@notif_registrar_review_request_created
@notif_accepted_email
@notif_accepted_within_aristotle
def review_request_created(recipient, obj, target):
    notify.send(obj, recipient=recipient, verb="requested concept review", target=target)


@notif_registrar_review_request_updated
@notif_accepted_email
@notif_accepted_within_aristotle
def review_request_updated(recipient, obj, target):
    notify.send(obj, recipient=recipient, verb="concept was reviewed", target=target)


@notif_issues_items_in_my_workgroups
@notif_accepted_email
@notif_accepted_within_aristotle
def issue_created_workgroup(recipient, obj):
    notify.send(obj, recipient=recipient, verb="(issue) has been created on the item", target=obj.item)


@notif_issues_items_in_my_workgroups
@notif_accepted_email
@notif_accepted_within_aristotle
def issue_comment_created_workgroup(recipient, obj):
    notify.send(obj.issue, recipient=recipient, verb="A new comment on an Issue has been created in the workgroup:", target=obj.issue.item.workgroup)


@notif_issues_favourited
@notif_accepted_email
@notif_accepted_within_aristotle
def issue_created_favourite(recipient, obj):
    notify.send(obj, recipient=recipient, verb="(issue) has been created on a favourite item:", target=obj.item)


@notif_issues_favourited
@notif_accepted_email
@notif_accepted_within_aristotle
def issue_comment_created_favourite(recipient, obj):
    notify.send(obj.issue, recipient=recipient, verb="A new comment has been created on an issue of a favourite item:", target=obj.issue.item)


@notif_issues_i_can_edit
@notif_accepted_email
@notif_accepted_within_aristotle
def issue_created_items_i_can_edit(recipient, obj):
    notify.send(obj, recipient=recipient, verb="(issue) has been created on an item you can edit:", target=obj.item)


@notif_issues_i_can_edit
@notif_accepted_email
@notif_accepted_within_aristotle
def issue_comment_created_items_i_can_edit(recipient, obj):
    notify.send(obj.issue, recipient=recipient, verb="A new comment has been created on an issue of an item you can edit:", target=obj.issue.item)


@notif_discussions_new_posts
@notif_accepted_email
@notif_accepted_within_aristotle
def new_post_created(recipient, post):
    if post.author:
        if post.workgroup is not None:
            notify.send(post, recipient=recipient, verb="(discussion) has been created in the workgroup:", target=post.workgroup)
        else:
            notify.send(post, recipient=recipient, verb="(discussion) has been created.")


@notif_discussions_new_comments
@notif_accepted_email
@notif_accepted_within_aristotle
def new_comment_created(recipient, comment):
    if comment.author:
        notify.send(comment, recipient=recipient, verb="(comment) has been created in the discussion:", target=comment.post)
