import 'src/vendor/jquery-ui.min.js'
import { addRow } from 'src/lib/formset.js'

import 'src/styles/aristotle.moveable.less'


function addCode(id) {
    addRow(id, 'tr')
    let table = $('#' + id)
    reorderRows(table);
}

function renumberRow(row,num) {
    var order_fields = $(row).find('input[name$="-ORDER"]')
    if (order_fields.length > 0) {
        order_fields.attr('value',num);
    } else {
        $(row).find('input[name$="-order"]').attr('value', num)
    }
}

function reorderRows(panelList) {
    $('.moveablerow', panelList).each(function(index) {
        renumberRow(this,index);
        $(this).find('input[name$=-DELETE]').attr('title',"Delete item "+index);
    });
}

export function initMoveable() {
    $('.draggableTable').each(function(){
        var thistable = $(this)
        $(this).sortable({
            // Only make the .panel-heading child elements support dragging.
            // Omit this to make the entire <li>...</li> draggable.
            handle: '.grabber',
            start: function () {
                $(this).addClass('info');
                $('.grabber').addClass('grabbed');
            },
            stop: function () {
                $('.grabber').removeClass('grabbed');
            },

            update: function() {
                reorderRows(thistable);
            }
        });
    })

    $('a.add_code_button').click(function() {
        addCode($(this).attr('formid'));
    });

    $("form").submit(function() {
        $(".draggableTable .moveablerow").each(function() {
            var row = this;
            if ($(row).find("input[name$=-id]").val() == "") {
                // For rows with a blank id (newly added)
                var all_empty = true;
                $(row).find(':input').each(function() {
                    var myclass = $(this).attr('class')
                    if (myclass != 'select2-search__field') {
                        var name = $(this).attr('name').split('-')[2];
                        if (name != 'ORDER' && name != 'DELETE') {
                            // We skip all uppercase ones as they are Django sepcial fields
                            all_empty = all_empty && ($(this).val() == "")
                        }
                    }
                })
                if (all_empty) {
                    // We could delete it, but that might be visually disturbing
                    // So lets just check deleted
                    $(row).find('input[name$=-DELETE]').val('on').prop('checked', 'on');
                }
            }
        })
    });
}
