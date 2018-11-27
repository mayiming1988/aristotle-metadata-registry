/* globals CKEDITOR */
import 'src/styles/ckeditor_plugins.css'
import { initDALWidget } from 'src/lib/dal_simple_init.js'

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
                let link_text = document.createTextNode(option.title)

                let link = document.createElement('a')
                link.className = 'aristotle-concept-link'
                link.href = '/item/' + g_id
                link.setAttribute('data-aristotle-concept-id', g_id)
                link.appendChild(link_text)
                editor.insertHtml(link.outerHTML);
            },
            onLoad: function() {
                // Initialize the select2 box
                initDALWidget($('.cke_dialog_body [data-autocomplete-light-function=select2]').first())
            }
        };
    });
}

function requestDialog(editor, url, addFunction) {
    $.ajax({
        url: url,
    })
    .done(function(data) {
        let dialog = $(data)

        dialog.find('input').addClass('cke_dialog_ui_input_text')
        dialog.find('label').addClass('cke_dialog_ui_labeled_label').css('display','block')

        addFunction(editor, dialog.html())
    });
}

export function addPlugins(editor) {
    let glossary_form_url = '/glossary/search_dialog/'
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
    requestDialog(editor, glossary_form_url, addGlossaryDialog)
}
