from django.db.models import Prefetch
from aristotle_mdr.contrib.links.models import Link, LinkEnd
from aristotle_mdr.models import _concept


def get_links_for_concept(concept):
    leqs = LinkEnd.objects.select_related('concept').select_related('role')
    links = Link.objects.filter(
        root_item=concept
    ).select_related(
        'relation'
    ).prefetch_related(
        Prefetch('linkend_set', queryset=leqs)
    )
    return links


def get_all_links_for_concept(concept, user):
    """Get all links for a concept that the user has permission to view"""
    leqs = LinkEnd.objects.select_related('concept').select_related('role')
    links = Link.objects.filter(
        linkend__concept=concept,
    ).select_related(
        'relation'
    ).prefetch_related(
        Prefetch('linkend_set', queryset=leqs)
    )
    # Restrict it down to only the visible concepts
    visible_concepts = set(_concept.objects.all().visible(user).values_list('pk', flat=True))
    for link in links:
        for linkend in link.linkend_set.all():
            if linkend.concept.pk not in visible_concepts:
                links = links.exclude(pk=link.pk)

    return links
