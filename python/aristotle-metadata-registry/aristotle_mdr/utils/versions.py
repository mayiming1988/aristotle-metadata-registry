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
        self.html = html

    @property
    def is_link(self):
        return self.link

    @property
    def is_group(self):
        return self.group

    @property
    def is_html(self):
        return self.html

    @property
    def heading(self):
        return self.fname

    def __str__(self):
        return self.value or 'None'


class VersionLinkField(VersionField):
    """Version field that links to a concept"""

    link = True
    group = False
    html = False
    perm_message = 'Linked to object you do not have permission to view'

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


class VersionGroupField(VersionField):
    """Field with groups of subfields"""
    link = False
    group = True
    html = False

    def __init__(self, fname: str, sub_fields: List[List[VersionField]]):
        self.fname = fname
        self.sub_fields = sub_fields

    @property
    def headings(self) -> List[str]:
        headings = []
        if self.sub_fields:
            for field in self.sub_fields[0]:
                headings.append(field.heading)
        return headings

    def __str__(self):
        return '{} sub items'.format(len(self.sub_fields))
