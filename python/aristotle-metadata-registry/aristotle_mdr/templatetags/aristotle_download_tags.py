# -*- coding: utf-8 -*-
"""
Tags and filters available in aristotle templates
=================================================

A number of convenience tags are available for performing common actions in custom
templates.

Include the aristotle template tags in every template that uses them, like so::

    {% load aristotle_download_tags %}

Available tags and filters
--------------------------
"""
from django import template
register = template.Library()


@register.filter
def rels_for_download(qs, user):
    if not user:
        return qs.public().prefetch_related("statuses")
    else:
        return qs.visible(user=user).prefetch_related("statuses")
