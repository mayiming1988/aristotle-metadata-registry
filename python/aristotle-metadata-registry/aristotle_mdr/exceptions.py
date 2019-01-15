class NoUserGivenForUserForm(Exception):
    """You are implementing the UserForm Mixin, but no user could be found."""


class BadDownloadModuleName(Exception):
    """You are trying to use a download name that isn't a valid Python module name."""


class BadDownloadTypeAbbreviation(Exception):
    """You are trying to use a download name that isn't a valid Python module name."""


class BadBulkActionModuleName(Exception):
    """You are trying to use a bulk action import that isn't a valid Python module name."""
