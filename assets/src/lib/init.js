import 'bootstrap'
import { initNotifications } from '../lib/notify.js'
import { initMessages } from '../lib/messages.js'

export function init(spinners = true) {
  // Scrap modals if they lose focus so they can be loaded with new content
  $('.modal').on('hidden.bs.modal', function(e)
  {
      if (!$(this).hasClass('exclude-scrap')) {
        $(this).removeData();
        x = $(this).find('.modal-content > *');
        x.remove()
      }
  });

  $('.modal').on('loaded.bs.modal', function() {
      // Need to do this on modal show for newly added popovers
      $('.aristotle-popover').popover()
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

  initNotifications()
  initMessages()

  if (spinners) {
    $(document).ajaxSend(function(event, request, settings) {
        $('#loading_indicator').show().addClass('loading').removeClass('hidden');
    });

    $(document).ajaxComplete(function(event, request, settings) {
        $('#loading_indicator').hide().removeClass('loading');
    });
  }
}
