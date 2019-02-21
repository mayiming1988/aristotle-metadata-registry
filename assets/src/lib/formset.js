import { initDALWidget } from './dal_simple_init.js'

export function replacePrefix(element, num_forms) {
    var name = $(element).attr('name')
    var id = $(element).attr('id')

    if (name && name.includes('__prefix__')) {
        var new_name = name.replace('__prefix__', num_forms)
        $(element).attr('name', new_name)
    }

    if (id && id.includes('__prefix__')) {
        var new_id = id.replace('__prefix__', num_forms)
        $(element).attr('id', new_id)
    }

}

// Adds a row to a formset given a form element and row css selector
export function addRow(formid, row_selector) {
    let panelList = $('#' + formid);
    let formstage = $('.formstage#' + formid + ' ' + row_selector)

    //Recreate the date time pickers
    //Get options from the formstage
    if (formstage.find('.date').data('DateTimePicker')) {
        var options = formstage.find('.date').data('DateTimePicker').options()
        //Initialize all date time objects
        new_form.find('.date').each(function() {
            $(this).datetimepicker(options);
        })
    }

    // Remove redundant select2s (they'll be remade when reinserted into the node)
    formstage.find('span.select2.select2-container').remove();

    let new_form = formstage.clone();

    var all_rows = panelList.find(row_selector)
    var num_forms = $(all_rows).length
    new_form.insertAfter(all_rows.last());

    new_form.find(':input').each(function() {
        replacePrefix(this, num_forms)
    });

    // rename the form entries
    let total_forms_identifier = 'input[name=' + formid + '-TOTAL_FORMS]'
    $(total_forms_identifier).val(num_forms+1);

    new_form.find('[data-autocomplete-light-function=select2]').each(function() {
        var element = $(this);
        initDALWidget(element)
    })
}

export default function initFormset() {
    $('a.add_code_button').click(function() {
        addRow($(this).attr('formid'), '.form-inline');
    });
}
