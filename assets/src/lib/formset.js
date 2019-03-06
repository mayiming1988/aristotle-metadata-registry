import { initDALWidget } from './dal_simple_init.js'
import { reinitCKEditors } from './ckeditor_simple_init.js'

export function replacePrefix(element, num_forms) {
    let name = $(element).attr('name')
    let id = $(element).attr('id')

    if (name && name.includes('__prefix__')) {
        let new_name = name.replace('__prefix__', num_forms)
        $(element).attr('name', new_name)
    }

    if (id && id.includes('__prefix__')) {
        let new_id = id.replace('__prefix__', num_forms)
        $(element).attr('id', new_id)
    }

}

// Adds a row to a formset given a form element and row css selector
// urlfunc is optional (used for dal init)
export function addRow(formid, row_selector, urlfunc) {
    let panelList = $('#' + formid);
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
    if (num_forms > 0) {
        // If there are existing forms insert after last one
        new_form.insertAfter(all_rows.last());
    } else {
        // If this is the first form
        let add_buttons = panelList.find('.add_code_button')
        if (add_buttons.length > 0) {
            // If an add button is in the panel list insert before that
            let button = add_buttons.first()
            new_form.insertBefore(button)
        } else {
            // otherwise just append to the panel list
            panelList.append(new_form)
        }
    }

    new_form.find(':input').each(function() {
        replacePrefix(this, num_forms)
    });

    // rename the form entries
    let total_forms_identifier = 'input[name=' + formid + '-TOTAL_FORMS]'
    $(total_forms_identifier).val(num_forms+1);

    new_form.find('[data-autocomplete-light-function=select2]').each(function() {
        let element = $(this);
        initDALWidget(element, urlfunc)
    })

    reinitCKEditors(new_form);
}

// initialize a general formset (urlfunc is optional)
export default function initFormset(urlfunc) {
    $('a.add_code_button').click(function() {
        addRow($(this).attr('formid'), '.form-inline', urlfunc);
    });
}
