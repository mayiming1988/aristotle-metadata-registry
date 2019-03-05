// Polyfills
import '@babel/polyfill' // This include required core-js modules
// mdn-polyfils for DOM API polyfills (core-js is only for js language features)
import 'mdn-polyfills/Element.prototype.closest'
// NodeList.forEach is used by django-debug-toolbar
// import 'mdn-polyfills/NodeList.prototype.forEach'

import 'bootstrap'
import 'eonasdan-bootstrap-datetimepicker'

import { initNotifications } from './notify.js'
import { initMessages } from './messages.js'
import { initDAL } from './dal_simple_init.js'
import { initCKEditor } from './ckeditor_simple_init.js'
import { initTime } from './localtime.js'

// Always on styles
import 'src/styles/bootstrap.less'
import 'font-awesome/css/font-awesome.css'
import 'src/styles/aristotle.less'
import 'src/styles/aristotle.print.less'
import 'src/styles/aristotle.visuals.less'
import 'src/styles/bootstrap.wcag.css'
import 'src/styles/pink.wcag.css'
import 'src/styles/aristotle.autocomplete.css'
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
}

export function initSpinners() {
    $(document).ajaxSend(() => {
        $('#loading_indicator').show().addClass('loading').removeClass('hidden');
    });

    $(document).ajaxComplete(() => {
        $('#loading_indicator').hide().removeClass('loading');
    });
}

export function initModalScrap() {
    // Needs to be run on document ready
    $(document).ready(function() {
        // Scrap modals if they lose focus so they can be loaded with new content
        $('.modal').on('hidden.bs.modal', function()
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

// This should be run on most pages
export function initCore() {
    initNotifications()
    initMessages()
    initTime()
}

// Init all function, only use if the page actually needs all this
export default function init() {
    initCore()
    initWidgets()
    initSpinners()
    initModalScrap()
}
