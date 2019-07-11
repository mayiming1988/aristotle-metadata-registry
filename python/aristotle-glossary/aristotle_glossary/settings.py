CKEDITOR_CONFIGS = {
    'default': {
         'toolbar': [
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', '-', 'Undo', 'Redo',]},
            {'name': 'basicstyles', 'items': ['Bold', 'Italic', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'links', 'items': ['Link', 'Unlink']},
            {'name': 'paragraph', 'items': ['NumberedList', '-', 'BulletedList', '-', 'Blockquote', '-', 'Indent',
                                            'Outdent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight']},
            {'name': 'insert', 'items': ['Image', 'Table', 'HorizontalRule', 'SpecialChar']},
            {'name': 'aristotletoolbar', 'items': ['Glossary']},
            {'name': 'document', 'items': ['Maximize', 'Source', 'Math']},
         ],
        'width': "",
        'disableNativeSpellChecker': False,
        # To enable extra plugins, add to extraPlugins.
        # Make sure you add the JS import to CkEditor plugins to actually import the additional plugin
        'extraPlugins': 'aristotle_glossary,justify',
        'customConfig' : '',
        'removePlugins': 'contextmenu,liststyle,tabletools,tableselection',
        'extraAllowedContent': 'a[data-aristotle-concept-id]'
    },
}