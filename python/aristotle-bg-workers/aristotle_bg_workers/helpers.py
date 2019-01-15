
# Helper functions
import logging
logger = logging.getLogger(__name__)


def date_convert(date):
    return date.strftime('%d/%m/%y %I:%M %p')


def get_pretty_name(name):
    if type(name) is str:
        # TODO
        if name.startswith("long__"):
            name = name[6:]
        return name.replace('_', ' ').title()
    else:
        return name
