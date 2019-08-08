from django.db.models import Prefetch
from aristotle_mdr.contrib.links.models import Link, LinkEnd


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


def get_all_links_for_concept(concept):
    leqs = LinkEnd.objects.select_related('concept').select_related('role')
    links = Link.objects.filter(
        # root_item=concept
        linkend__concept=concept
    ).select_related(
        'relation'
    ).prefetch_related(
        Prefetch('linkend_set', queryset=leqs)
    )
    return links
