from typing import Union, List
from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.html import format_html
from django.utils.safestring import mark_safe, SafeString
from django.conf import settings
from django.db.models import Model

from aristotle_mdr.utils.text import pretify_camel_case
from aristotle_mdr.structs import Breadcrumb

import bleach
import json
import dateutil
from datetime import datetime, date

register = template.Library()


@register.filter
def getdir(obj):
    return dir(obj)


@register.filter
def order_by(qs, order):
    return qs.order_by(*(order.split(",")))


@register.filter
def startswith(string, substr):
    return string.startswith(substr)


@register.filter
def visible_count(model, user):
    return type(model).objects.all().visible(user).count()


@register.filter
def izip(a, b):
    return zip(a, b)


@register.filter
def register_queryset(qs):
    from aristotle_mdr.utils.cached_querysets import register_queryset
    return register_queryset(qs)


@register.filter
def distinct(iterable, attr_name):

    if not iterable:
        return []

    seen = []
    filtered = []
    for item in iterable:
        attr = getattr(item, attr_name)
        if attr not in seen:
            filtered.append(item)
            seen.append(attr)

    return filtered


@register.filter(name='bleach')
def bleach_filter(html: str) -> SafeString:
    """Clean a html string before it is rendered"""
    # If trying to bleach a none just return it
    if html is None:
        return html
    # Remove tags and attr based on settings
    clean_html = bleach.clean(
        html,
        tags=settings.BLEACH_ALLOWED_TAGS,
        attributes=settings.BLEACH_ALLOWED_ATTRIBUTES,
        strip=True,  # Remove disallowed tags instead of escaping them
        strip_comments=True,
    )
    # Wrap html so we can style it & make sure it isnt rendered by vue
    wrapped_html = '<div v-pre class="bleached-content">' + clean_html + '</div>'
    # Return Wrapped html as safe string
    return mark_safe(wrapped_html)


@register.filter
def class_name(obj) -> str:
    # Obj can be a class or and instance
    if isinstance(obj, object):
        obj = type(obj)
    name = obj.__name__
    return pretify_camel_case(name)


@register.filter(name='isotime')
def iso_time(dt: Union[datetime, date, None]):
    """Return ISO 8601 string from datetime object"""
    if dt is None:
        return '-'

    dtype = type(dt)
    if dtype in (datetime, date):
        return dt.isoformat()
    else:
        # If we got a non datetime or date object don't do anything
        return dt


@register.filter
def lookup_string(mapping, key):
    return mapping.get(key, '')


@register.filter
def get_custom_values_for_item(item, user):
    from aristotle_mdr.contrib.custom_fields.models import CustomField, CustomValue
    allowed = CustomField.objects.get_allowed_fields(item.concept, user)
    custom_values = CustomValue.objects.get_allowed_for_item(item.concept, allowed)
    not_empty_custom_values = []
    for value in custom_values:
        if value.content:
            not_empty_custom_values.append(value)
    return not_empty_custom_values


@register.filter
def as_str(item):
    return str(item)


def format_time(dt, html_format):
    """Format html with dates inserted
    Helper function used by timetag and timefromtag"""
    if dt is None:
        return '-'

    elif type(dt) in (datetime, date):
        # ISO format to be parsed by js
        isotime = dt.isoformat()
        # Format to use when js replacement fails
        nicetime = dt.strftime('%d %B %Y')

        return format_html(
            html_format,
            isotime=isotime,
            time=nicetime
        )

    # If we got an invalid type return initial value
    return dt


@register.simple_tag
def timetag(dt: Union[datetime, date, None]):
    """Render time element for use with js local time replacement"""
    return format_time(dt, '<time datetime="{isotime}">{time}</time>')


@register.simple_tag
def timefromtag(dt: Union[datetime, date, None]):
    """Same as timetag above, but will show time from now
    e.g. 4 Days Ago"""
    return format_time(dt, '<time datetime="{isotime}" data-time-from="true">{time}</time>')


@register.simple_tag(name='lookup')
def dict_lookup(mapping, *keys):
    """
    Get a value from dictionary of any depth
    Return empty string if an error is encountered
    Usage: {% lookup dict key1 key2 ... %}
    """

    if type(mapping) == str:
        json.load(mapping)

    result = mapping
    for key in keys:
        try:
            result = result[key]
        except (KeyError, TypeError) as e:
            # If key was not found or object is not indexable
            # In development raise error, in production return empty string
            if settings.DEBUG:
                raise e
            else:
                return ''

    return result


@register.simple_tag(name='lookup_or')
def dict_lookup_or(mapping, key, default):
    """Return value in mapping or a default
    Useful when using a mapping of cached values"""
    if key in mapping:
        return mapping[key]

    return default


@register.inclusion_tag('aristotle_mdr/helpers/breadcrumbs.html')
def breadcrumb_list(crumbs: List[Breadcrumb]):
    return {'breadcrumbs': crumbs}


@register.filter
def pluralize_model(count: int, model: Model):
    """Return verbose name or plural verbose name, depending on a count"""
    if count > 1:
        return model._meta.verbose_name_plural.title()

    return model._meta.verbose_name.title()


@register.filter
def model_verbose_name(model):
    return model._meta.verbose_name.title()


@register.filter
def model_verbose_name_plural(model):
    return model._meta.verbose_name_plural.title()


@register.simple_tag()
def assign(string):
    return string


@register.filter
def parse_date(date: str) -> datetime:
    """Parse iso 8601 date string into datetime object"""
    # Can be replace with .fromisoformat in python 3.7
    return dateutil.parser.parse(date)
