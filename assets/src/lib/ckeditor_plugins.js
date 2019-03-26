/* globals CKEDITOR */
import 'src/styles/ckeditor_plugins.css'
import { initDALWidget } from 'src/lib/dal_simple_init.js'
import { buildElement } from 'src/lib/html.js'

function buildDialogHtml(item_label, select_id, dalurl) {
    let final_label = item_label + ':'
    let div = document.createElement('div')
    let select2box = buildElement('select', {
        id: select_id,
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
        {for: select_id},
        final_label 
    )
    select2box.appendChild(option)
    div.appendChild(label)
    div.appendChild(select2box)
    return div.outerHTML
}

function addDialog(editor, dialogname, dialogtitle, dialoghtml, select_id) {
    editor.dialog.add(dialogname, function(editor) {
        return {
            title : dialogtitle,
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
                let select = document.getElementById(select_id)
                let option = select.options[select.selectedIndex]
                let g_id = option.value
                if (g_id) {
                    let g_name = option.title

                    let linkattrs = {
                        class: 'aristotle-concept-link',
                        href: '/item/' + g_id,
                        'data-aristotle-concept-id': g_id
                    }
                    let link = buildElement('a', linkattrs, g_name)
                    editor.insertHtml(link.outerHTML);
                }
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
    let html = buildDialogHtml(
        'Glossary Item', 
        'id_glossary',
        '/ac/concept/aristotle_glossary-glossaryitem?public=1'
    )
    addDialog(editor, 'glossaryListDialog', 'Glossary search', html, 'id_glossary')
}

export function addPluginConfig(config) {
    // Add to config to enable plugin
    config.extraPlugins = 'aristotle_glossary'
    let last_bar = config.toolbar.pop()
    config.toolbar.push({name: 'aristotletoolbar', items: ['Glossary']})
    if (last_bar != undefined) {
        config.toolbar.push(last_bar)
    }
}
