function reorder(widget) {
    let count = 0;
    widget.find('input:not(:last)').each(function() {
        let split_name = $(this).attr('name').split('-')
        let split_id = $(this).attr('id').split('-')
        $(this).attr('name', split_name[0] + '-' + count.toString())
        $(this).attr('id', split_id[0] + '-' + count.toString())
        count += 1
    })
}

function remove_field(button) {
    let widget = $(button).closest('.multi-widget')
    let count = widget.find('.form-group').length
    if (count > 1) {
        $(button).closest('.form-group').remove()
    } else {
        // If removing last field disable and hide instead
        $(button).closest('.form-group').hide()
        let input = $(button).closest('.form-group').find('input')
        input.val('')
        // disabling stops it from being submitted
        input.prop('disabled', true)
    }
    reorder(widget)
    $("#update-alert-id").slideDown()
}

function add_field(button) {

    let widget = $(button).closest('.multi-widget')
    let email = widget.find('#email-input-id').val()
    let nextElementIndex = widget.find('.multi-fields').children().length + 1;

    if (isEmailValid(email)) {
        if (isEmailDuplicated(email)) {
            let alert = widget.find("#duplicated-email-alert-id")
            alert.slideDown()
            setTimeout(function () {
                alert.slideUp()
            }, 3000)
        } else {
            widget.find('.multi-fields').append(
                '<div class="form-group text-success">' +
            email +
            '<div class="hidden">' +
            '<input type="email" name="emails-'+ nextElementIndex +'" value="' + email + '" class="form-control"' +
            'id="id_emails-' + nextElementIndex + '">' +
            '</div>' +
            '<button type="button" class="btn btn-sm btn-danger remove-field widget-button pull-right" title="Remove ' + email +'">' +
            '<i class="fa fa-times fa-fw"></i>' +
            '</button>' +
            '</div>'
        )

        widget.find('#email-input-id').val("")
        widget.find("#update-alert-id").slideDown()
        }

    } else {
        let alert = widget.find("#alert-email-id")
        alert.slideDown()
        setTimeout(function () {
            alert.slideUp()
        }, 3000)
    }
}

function isEmailValid(email) {
    var re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

function isEmailDuplicated(email) {
    let result = false;
    $('.form-group').each(function () {
        if (email === $(this).find('.hidden').find('input').val()) {
            result = true
            return false
        }
    })
    return result
}

function remove_all(button) {
    let widget = $(button).closest('.multi-widget')
    widget.find('.remove-field').each(function() {
        remove_field(this)
    })
}

function update_fields() {
    $('.form-group').removeClass('text-success')
    $("#update-alert-id").slideUp()
    setTimeout(function () {
        $('.ajax-success').slideUp('slow', function () {
            $('.ajax-success').remove()
        })
    }, 3000)
}

export function initMultifield() {
    $('.add-field').click(function() {
        add_field(this);
    })

    $(document).on('click', '.remove-field', function () {
        remove_field(this)
    })

    $('.remove-all').click(function() {
        remove_all(this)
    })

    $('#submit-button-id').click(function () {
        update_fields(this)
    })
}
