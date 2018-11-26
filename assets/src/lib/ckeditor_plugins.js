/* globals CKEDITOR */
import 'src/styles/ckeditor_plugins.css'
import { initDALWidget } from 'src/lib/dal_simple_init.js'

function addDialog(editor, dialoghtml) {
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
                let link_text = option.title

                let content = '<a class="aristotle_glossary" data-aristotle-glossary-id="'+g_id+'" href="/item/'+g_id+'">' + link_text + '</a>';
                editor.insertHtml(content, 'unfiltered_html');
            },
            onLoad: function() {
                // Initialize the select2 box
                initDALWidget($('.cke_dialog_body [data-autocomplete-light-function=select2]').first())
            }
        };
    });
}

function requestGlossary(editor) {
    $.ajax({
        url:'/glossary/search_dialog/',
    })
    .done(function(data) {
        let dialog = $(data)

        dialog.find('input').addClass('cke_dialog_ui_input_text')
        dialog.find('label').addClass('cke_dialog_ui_labeled_label').css('display','block')

        addDialog(editor, dialog.html())
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
    requestGlossary(editor)
}
