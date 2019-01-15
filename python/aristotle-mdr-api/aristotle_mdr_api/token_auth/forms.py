from django.forms import Form
from django.forms.fields import CharField
from django_jsonforms.forms import JSONSchemaField

class TokenCreateForm(Form):

    name = CharField(max_length=100)
    perm_json = JSONSchemaField(
        schema = {
            'type': 'object',
            'title': 'Permissions',
            'properties': {
                'metadata': {
                    'type': 'object',
                    'title': 'Metadata',
                    'description': 'Metadata',
                    'properties': {
                        'read': {
                            'title': 'Read',
                            'type': 'boolean',
                            'format': 'checkbox'
                        },
                        'write': {
                            'title': 'Write',
                            'type': 'boolean',
                            'format': 'checkbox'
                        }
                    }
                },
                'search': {
                    'type': 'object',
                    'title': 'Search',
                    'description': 'Search Metadata',
                    'properties': {
                        'read': {
                            'title': 'Read',
                            'type': 'boolean',
                            'format': 'checkbox'
                        }
                    }
                },
                'organization': {
                    'type': 'object',
                    'title': 'Organization',
                    'description': 'Organization Access',
                    'properties': {
                        'read': {
                            'title': 'Read',
                            'type': 'boolean',
                            'format': 'checkbox'
                        }
                    }
                },
                'ra': {
                    'type': 'object',
                    'title': 'Registration Authority',
                    'description': 'Registration Authority Access',
                    'properties': {
                        'read': {
                            'title': 'Read',
                            'type': 'boolean',
                            'format': 'checkbox'
                        }
                    }
                }
            }
        },
        options={
            'theme': 'bootstrap3',
            'disable_properties': True,
            'disable_collapse': True,
            'disable_edit_json': True,
            'no_additional_properties': True
        },
        label=''
    )
