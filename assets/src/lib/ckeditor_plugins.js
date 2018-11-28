/* globals CKEDITOR */
import 'src/styles/ckeditor_plugins.css'
import { initDALWidget } from 'src/lib/dal_simple_init.js'
import { buildElement } from 'src/lib/html.js'

function buildDialogHtml(item_label, dalurl) {
    let final_label = item_label + ':'
    let div = document.createElement('div')
    let select2box = buildElement('select', {
        id: 'id_items',
        class: 'aristotle-select2',
        name: 'items',
        required: '',
        'data-html': 'true',
        'data-autocomplete-light-url': dalurl,
        'data-autocomplete-light-function': 'select2'
    })
    let option = buildElement(
        'option', 
        {value: '', selected: ''},
        '---------'
    )
    let label = buildElement(
        'label', 
        {for: 'id_items'},
        final_label 
    )
    select2box.appendChild(option)
    div.appendChild(label)
    div.appendChild(select2box)
    return div.outerHTML
}

function addGlossaryDialog(editor, dialoghtml) {
    editor.dialog.add('glossaryListDialog', function(editor) {
        return {
            title : 'Glossary search',
            minWidth : 400,
            minHeight : 200,
            contents :
            [
                {
                    id: 'general',
                    label: 'Settings',
                    elements: [
                        {
                            type : 'html',
                            html : dialoghtml,
                        }
                    ]
                }
            ],
            onOk: function() {
                let select = document.querySelector('#id_items')
                let option = select.options[select.selectedIndex]
                let g_id = option.value
                let g_name = option.title

                let linkattrs = {
                    class: 'aristotle-concept-link',
                    href: '/item/' + g_id,
                    'data-aristotle-concept-id': g_id
                }
                let link = buildElement('a', linkattrs, g_name)
                editor.insertHtml(link.outerHTML);
            },
            onLoad: function() {
                // Initialize the select2 box
                initDALWidget($('.cke_dialog_body [data-autocomplete-light-function=select2]').first())
            }
        };
    });
}

export function addPlugins(editor) {
    editor.plugins.add('aristotle_glossary', {
        icons: 'glossary',
        init: function( editor ) {
            editor.addCommand('insertGlossary', new CKEDITOR.dialogCommand('glossaryListDialog'))

            editor.ui.addButton( 'Glossary', {
                label: 'Insert glossary item',
                command: 'insertGlossary',
            });
        }
    });
    let html = buildDialogHtml('Glossary Item', '/ac/concept/aristotle_glossary-glossaryitem')
    addGlossaryDialog(editor, html)
}
