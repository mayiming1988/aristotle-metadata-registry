import 'bootstrap'
import 'eonasdan-bootstrap-datetimepicker'
import '@babel/polyfill'
import { initNotifications } from './notify.js'
import { initMessages } from './messages.js'
import { initDAL } from './dal_simple_init.js'
import { initCKEditor } from './ckeditor_simple_init.js'
import { initMoveable } from './moveable.js'

// Always on styles
import 'bootstrap/dist/css/bootstrap.css'
import 'font-awesome/css/font-awesome.css'
import '../styles/aristotle.less'
import '../styles/aristotle.visuals.less'
import '../styles/bootstrap.wcag.css'
import '../styles/pink.wcag.css'
import 'eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.css'

export function initWidgets() {
  // Initialize popovers
  $('.aristotle-popover').popover()

  // Initialize datepickers
  $('.dj-datepicker').each((index, obj) => {
    obj = $(obj)
    var options = obj.attr('options')
    if (options == undefined) {
      options = {format: 'YYYY-MM-DD'}
    } else {
      options = JSON.parse(options)
    }
    obj.datetimepicker(options)
  })
  
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

  // Initialize django-autocomplete-light
  initDAL()

  // Initialize ckeditor
  initCKEditor()

  // Initialize moveable
  initMoveable()
}

export function initSpinners() {
  $(document).ajaxSend((event, request, settings) => {
      $('#loading_indicator').show().addClass('loading').removeClass('hidden');
  });

  $(document).ajaxComplete((event, request, settings) => {
      $('#loading_indicator').hide().removeClass('loading');
  });
}

export function initModalScrap() {
  // Needs to be run on document ready
  $(document).ready(function() {
    // Scrap modals if they lose focus so they can be loaded with new content
    $('.modal').on('hidden.bs.modal', function(e)
    {
        if (!$(this).hasClass('exclude-scrap')) {
          $(this).removeData();
          var x = $(this).find('.modal-content > *');
          x.remove()
        }
    });

    $('.modal').on('loaded.bs.modal', function() {
        // Need to do this on modal show for newly added popovers
        $('.dj-datepicker').datetimepicker({format: 'YYYY-MM-DD'})
        $('.aristotle-popover').popover()
    });

  })
}

// Init all function
export default function init(spinners = true) {

  initNotifications()
  initMessages()
  initWidgets()

  if (spinners) {
    initSpinners()
  }

  initModalScrap()

}
