import 'bootstrap'
import 'eonasdan-bootstrap-datetimepicker'
//import '@babel/polyfill'
import { initNotifications } from './notify.js'
import { initMessages } from './messages.js'
import { initDAL } from './dal_simple_init.js'
import { initCKEditor } from './ckeditor_simple_init.js'

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
  $('.dj-datepicker').datetimepicker({format: 'YYYY-MM-DD'})

  // Initialize django-autocomplete-light
  initDAL()

  // Initialize ckeditor
  initCKEditor()
}

export default function init(spinners = true) {

  var map = new Map()
  map.set('hello', 21)
  console.log(map)

  // Initialize popovers
  $('.aristotle-popover').popover()

  // Initialize datepickers
  $('.dj-datepicker').datetimepicker({format: 'YYYY-MM-DD'})

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
  initWidgets()

  if (spinners) {
    $(document).ajaxSend((event, request, settings) => {
        $('#loading_indicator').show().addClass('loading').removeClass('hidden');
    });

    $(document).ajaxComplete((event, request, settings) => {
        $('#loading_indicator').hide().removeClass('loading');
    });
  }

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
