$(document).ready(function() {
  function reorder(widget) {
    var count = 0;
    widget.find('input').each(function() {
      var split_name = $(this).attr('name').split('-')
      var split_id = $(this).attr('id').split('-')
      $(this).attr('name', split_name[0] + '-' + count.toString())
      $(this).attr('id', split_id[0] + '-' + count.toString())
      count += 1
    })
  }


  function disable_check(widget) {
    var count = widget.find('.form-group').length
    var button = widget.find('.remove-field').first()
    if (count == 1) {
      button.prop('disabled', true)
    } else if (count > 1) {
      button.prop('disabled', false)
    }
  }

  function remove_field(button) {
    var widget = $(button).closest('.multi-widget')
    $(button).closest('.form-group').remove()
    disable_check(widget)
    reorder(widget)
  }

  function emailPaste(e) {
    // Prevent the default pasting event and stop bubbling
    e.preventDefault();
    e.stopPropagation();

    // Get the clipboard data
    var paste = e.originalEvent.clipboardData.getData('text')

    // Get this widgets button
    var widget = $(e.target).closest('.multi-widget')
    var button = widget.find('.add-field')

    var emails = paste.split(',')
    for (var i=0; i < emails.length; i++) {
      var email = emails[i]
      if (i == 0) {
        $(e.target).val(email)
      } else {
        add_field(button, email)
      }
    }
  }

  function add_field(button, added_value='') {
    var widget = $(button).closest('.multi-widget')
    var fields = widget.find('.multi-fields').first()
    var clone = fields.find('.form-group').first().clone()
    var button = clone.find('.remove-field').first()
    
    button.prop('disabled', false)
    button.click(function() {
      remove_field(this)
    })

    var inputbox = clone.find('input')
    inputbox.val(added_value)
    inputbox.on('paste', emailPaste)

    clone.appendTo(fields)
    disable_check(widget)
    reorder(widget)
  }


  $('.add-field').click(function() {
    add_field(this);
  })

  $('.remove-field').click(function() {
    remove_field(this);
  })

  $('.multi-widget').each(function() {
    var widget = $(this)
    disable_check(widget)
  })
})
