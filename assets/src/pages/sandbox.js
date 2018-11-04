import { initCore } from '../lib/init.js'
import { ajaxForm } from '../lib/ajaxforms.js'
import { initMultifield } from '../lib/multifield.js'
import ClipboardJS from 'clipboard'

initCore()
initMultifield()

$(document).ready(function() {

    ajaxForm()

    var item_id;
    var button;
    var message_p = $('#modal-message')
    var csrftoken = $("[name=csrfmiddlewaretoken]").val(); // Can do this since a token is already on the page

    // Remove href attributes if javascript enabled
    // This will not be needed if using bootstrap 4.0
    $('.delete-button').each(function() {
        $(this).removeAttr('href');
    })

    $('#delete-modal').on('show.bs.modal', function(event) {
        button = $(event.relatedTarget);
        // Extract info from data-* attributes
        item_id = button.data('item-id') 
        var item_name = button.data('item-name') 
        message_p.html('Are you sure you want to delete ' + item_name + '?')
    })

    $('#delete-confirm-button').click(function() {
        $.ajax({
            method: "POST",
            url: delete_submit_url,
            data: {item: item_id, csrfmiddlewaretoken: csrftoken},
            datatype: "json",
            success: function(data) {
                if (data.completed) {
                    // Remove item's row
                    button.closest('tr').remove();
                    $('#delete-modal').modal('hide');
                } else if (data.message) {
                    message_p.html(data.message);
                }
            },
            error: function() {
                message_p.html("The item could not be deleted");
            }
        })
    })

    if (ClipboardJS.isSupported()) {
        new ClipboardJS('.copybutton');
    } else {
        $('.copybutton').remove()
    }

    $('.modal').on('hidden.bs.modal', function() {
        // On modal close remove ajax messages
        $('.ajax-error').remove()
        $('.ajax-success').remove()
    })
})
