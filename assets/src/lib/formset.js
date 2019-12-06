import { initDALWidget } from './dal_simple_init.js'
import { reinitCKEditors } from './ckeditor_simple_init.js'
import { reorderRows } from 'src/lib/moveable.js'

/* Replace __prefix__ with the form number in an elements attributes */
export function replacePrefix(element, num_forms) {
    if (element.hasAttributes()) {
        // Using .attributes instead of getAttributeNames for IE11 compatibility
        let attrs = element.attributes
        for (let i = 0; i < attrs.length; i++) {
            let name = attrs[i].name
            let value = attrs[i].value
            let newval = value.replace('__prefix__', num_forms)
            if (value !== newval) {
                attrs[i].value = newval
            }
        }
    }
}

// Adds a row to a formset given a form element and row css selector
// urlfunc is optional (used for dal init)

// To set up a dynamically added formset
// 1. Create a formset
// 2. Add a formstage
// 3. Add an add_code_button

export function addRow(formid, row_selector, urlfunc) {
    // The panelList is the formset
    let panelList = document.getElementById(formid)

    if (panelList.tagName === 'TABLE') {
        // If it's a table use the body
        panelList = panelList.querySelector('tbody')
    } else if (panelList.tagName === 'FORM') {
        // If panelList is a form and has a form-list class use that
        let list = panelList.querySelector('.form-list')
        if (list !== null) {
            panelList = list
        }
    }
    // Convert to jquery object
    panelList = $(panelList)

    // Important note: formid is the actual **id** of the formstage not 'formid'. This is set by django depending
    // on the model
    let formstage = $('.formstage#' + formid + ' ' + row_selector)

    // Clone the formstage
    let new_form = formstage.clone();

    // Recreate the date time pickers
    // Get options from the formstage
    if (formstage.find('.date').data('DateTimePicker')) {
        let options = formstage.find('.date').data('DateTimePicker').options()
        //Initialize all date time objects
        new_form.find('.date').each(function() {
            $(this).datetimepicker(options);
        })
    }

    // Remove redundant select2s (they'll be remade when reinserted into the node)
    formstage.find('span.select2.select2-container').remove();

    let all_rows = panelList.find(row_selector)
    let num_forms = all_rows.length

    // Append form to the panel list
    panelList.append(new_form)

    new_form.find(':input, div, button').each(function() {
        replacePrefix(this, num_forms)
    });

    // rename the form entries
    let total_forms_identifier = 'input[name=' + formid + '-TOTAL_FORMS]'
    $(total_forms_identifier).val(num_forms+1);

    new_form.find('[data-autocomplete-light-function=select2]').each(function() {
        let element = $(this);
        initDALWidget(element, urlfunc)
    })
    reorderRows(panelList);
    reinitCKEditors(new_form);
}

// Initialize a general formset (urlfunc is optional)
export default function initFormset(urlfunc) {
    $('a.add_code_button').click(function() {
        addRow($(this).attr('formid'), '.form-inline', urlfunc);
    });
}
