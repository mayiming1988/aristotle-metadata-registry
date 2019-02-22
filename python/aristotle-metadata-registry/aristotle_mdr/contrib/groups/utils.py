from django.contrib.auth.tokens import PasswordResetTokenGenerator

# Generating one-time links with django
# https://simpleisbetterthancomplex.com/tutorial/2016/08/24/how-to-create-one-time-link.html
# https://web.archive.org/web/*/https://simpleisbetterthancomplex.com/tutorial/2016/08/24/how-to-create-one-time-link.html


class GroupRegistrationTokenGenerator(PasswordResetTokenGenerator):
    def __init__(self, group):
        self.group = group

    def _make_hash_value(self, user, timestamp):
        """
        Hash the user's primary key and some user state that's sure to change
        after a password reset to produce a token that invalidated when it's
        used:

        1. The group the user is invited to (the user can't use another group id
            to spoof an invite to another group)
        2. The number of memberships they have in that group. This is usually 0,
            and after accepting the invite it will be 1.

        Note: after they accept the invitation it won't work again - however,
        if they are removed from the group in the TIMEOUT_DAYS period they will
        be able to rejoin the group in that period.

        For new users we could use last login to invalidate the key (as they'll
        be setting up a new account), but for existing users accepting an
        invite this won't work - we could force them to login to accept an invite

        But thats a challenge for later.
        """
        # Truncate microseconds so that tokens are consistent even if the
        # database doesn't support microseconds.
        current_role_count = int(self.group.members.filter(user=user).count())
        return str(user.pk) + str(self.group.pk) + str(current_role_count)
