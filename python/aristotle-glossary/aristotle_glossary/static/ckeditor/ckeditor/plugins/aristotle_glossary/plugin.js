function addDialog(dialoghtml) {
    CKEDITOR.dialog.add( 'glossaryListDialog', function( editor ) {
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
                var g_id = $('#id_items').val()
                var link_text = $('#id_link').val();

                content = '<a class="aristotle_glossary" data-aristotle-glossary-id="'+g_id+'" href="/item/'+g_id+'">' + link_text + '</a>';
                editor.insertHtml( content,"unfiltered_html" );
            }
        };
    });
}

function addGlossaryItemDialog () {
    $.ajax({
        url:'/glossary/search_dialog/',
    })
    .done(function( data ) {
        dialog = $(data)

        dialog.find('input').addClass('cke_dialog_ui_input_text')
        dialog.find('label').addClass('cke_dialog_ui_labeled_label').css('display','block')

        addDialog(dialog.html())
    });
}

CKEDITOR.plugins.add('aristotle_glossary', {
    icons: 'glossary',
    init: function( editor ) {
        editor.addCommand('insertGlossary', new CKEDITOR.dialogCommand('glossaryListDialog'))

        editor.ui.addButton( 'Glossary', {
            label: 'Insert glossary item',
            command: 'insertGlossary',
        });
    }
});
addGlossaryItemDialog()
