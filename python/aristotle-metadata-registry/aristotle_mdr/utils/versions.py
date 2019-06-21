from typing import List, Optional
from django.urls import reverse


class VersionField:
    """
    Field for use in previous version display
    Template to render in helpers/version_field.html
    """

    link: bool = False
    group: bool = False

    def __init__(self, fname: str, value, html=False):
        self.fname = fname
        self.value = str(value)
        self.is_html = html

    @property
    def is_link(self):
        return self.link

    @property
    def is_group(self):
        return self.group

    @property
    def heading(self):
        return self.fname

    def __str__(self):
        return self.value or 'None'


class VersionGroupField(VersionField):
    """Field with groups of subfields"""
    link = False
    group = True
    is_html = False

    def __init__(self, fname: str, subfields: List[List[VersionField]]):
        self.fname = fname
        self.subfields = subfields

    def __str__(self):
        return '{} sub items'.format(len(self.subfields))


class VersionLinkField(VersionField):
    """Version field that links to a concept or concept subclass"""

    link = True
    group = False
    is_html = False
    perm_message = 'Linked to object you do not have permission to view'
    subfields: List = []

    def __init__(self, fname: str, id: Optional[int], concept):
        self.fname = fname
        self.id = id

        if id is not None:
            if concept:
                # If field is set and we got a concept
                self.value = concept.name
                self.id = concept.id
            else:
                # If field is set but concept is None no perm
                self.value = self.perm_message
        else:
            # Set value empty if id is None
            self.value = ''

    @property
    def url(self):
        if self.id:
            return reverse('aristotle:item', args=[self.id])
        return ''
