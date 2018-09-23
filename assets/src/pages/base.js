import 'bootstrap'
import { reload_notifications } from '../lib/notify.js'

// Set (then unset) this to supress the ajax loading animation
var suppressLoadingBlock = false;

// Scrap modals if they lose focus so they can be loaded with new content
$('.modal').on('hidden.bs.modal', function(e)
{
    if (!$(this).hasClass('exclude-scrap')) {
      $(this).removeData();
      x = $(this).find('.modal-content > *');
      //console.log(x)
      x.remove()
    }
});

$('.modal').on('loaded.bs.modal', function() {
    $('.aristotle-popover').popover()
    // Need to do this on modal show for newly added popovers
});

// Initialize popovers
$('.aristotle-popover').popover()

//Initialise delete checkboxes
$('.delete-disable').click(function() {
  var deletebox = $(this)
  var checked = deletebox.prop('checked')
  var form = deletebox.closest('form')
  form.find('input').each(function() {
    if ($(this).attr('id') != deletebox.attr('id') && $(this).attr('name') != 'csrfmiddlewaretoken') {
      $(this).prop('disabled', checked)
    }
  })
  form.find('.widget-button').each(function() {
    $(this).prop('disabled', checked)
  })
})

$('#header_menu_button_notifications').click(reload_notifications)


$(document).ajaxSend(function(event, request, settings) {
    if (!suppressLoadingBlock) {
        $('#loading_indicator').show().addClass('loading').removeClass('hidden');
    }
});

$(document).ajaxComplete(function(event, request, settings) {
    $('#loading_indicator').hide().removeClass('loading');
});
