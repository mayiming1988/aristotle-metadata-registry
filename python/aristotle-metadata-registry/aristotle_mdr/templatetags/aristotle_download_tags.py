# -*- coding: utf-8 -*-
"""
Tags and filters available in aristotle templates
=================================================

A number of convenience tags are available for performing common actions in custom
templates.

Include the aristotle template tags in every template that uses them, like so::

    {% load aristotle_tags %}

Available tags and filters
--------------------------
"""
from django import template
from django.template.loader import get_template
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe

from aristotle_mdr import perms
import aristotle_mdr.models as MDR
from aristotle_mdr.utils import (
    fetch_metadata_apps,
    fetch_aristotle_downloaders
)
from aristotle_mdr.models import STATES

register = template.Library()


@register.filter
def rels_for_download(qs):
    return qs.public().prefetch_related("statuses")
