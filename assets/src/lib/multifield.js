function reorder(widget) {
    let count = 0;
    widget.find('input').each(function() {
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
        // If removing last field disbale and hide instead
        $(button).closest('.form-group').hide()
        let input = $(button).closest('.form-group').find('input')
        input.val('')
        // disabling stops it from being submitted
        input.prop('disabled', true)
    }
    reorder(widget)
}

function paste_handler(e) {
    // Prevent the default pasting event and stop bubbling
    e.preventDefault();
    e.stopPropagation();

    // Get the clipboard data
    let paste = e.originalEvent.clipboardData.getData('text')

    // Get this widgets button
    let widget = $(e.target).closest('.multi-widget')
    let button = widget.find('.add-field')

    let emails = paste.split(',')
    for (let i=0; i < emails.length; i++) {
        let email = emails[i]
        if (i == 0) {
            $(e.target).val(email)
        } else {
            add_field(button, email)
        }
    }
}

function add_field(button, added_value='') {
    let widget = $(button).closest('.multi-widget')
    //let count = widget.find('.form-group').length
    let fields = widget.find('.multi-fields').first()
    let firstgroup = widget.find('.form-group').first()

    if (firstgroup.is(':visible')) {
        let clone = fields.find('.form-group').first().clone()
        let button = clone.find('.remove-field').first()
        button.prop('disabled', false)
        button.click(function() {
            remove_field(this)
        })

        let inputbox = clone.find('input')
        inputbox.val(added_value)
        inputbox.on('paste', paste_handler)

        clone.appendTo(fields)
        reorder(widget)
    } else {
        // If first group was disabled, show it enable input
        firstgroup.show()
        firstgroup.find('input').prop('disabled', false)
    }
}

function remove_all(button) {
    let widget = $(button).closest('.multi-widget')
    widget.find('.remove-field').each(function() {
        remove_field(this)
    })
}


export function initMultifield() {
    $('.add-field').click(function() {
        add_field(this);
    })

    $('.remove-field').click(function() {
        remove_field(this);
    })

    $('.remove-all').click(function() {
        remove_all(this);
    })
}
