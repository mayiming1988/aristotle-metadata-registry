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
    // Can be run after remove and add and startup to prevent deleting last row
    // Not currently used
    var count = widget.find('.form-group').length
    var button = widget.find('.remove-field').first()
    var input = widget.find('input').first()
    if (count == 1) {
      button.prop('disabled', true)
    } else if (count > 1) {
      button.prop('disabled', false)
    }
  }

  function remove_field(button) {
    var widget = $(button).closest('.multi-widget')
    var count = widget.find('.form-group').length
    if (count > 1) {
      $(button).closest('.form-group').remove()
    } else {
      // If removing last field disbale and hide instead
      $(button).closest('.form-group').hide()
      var input = $(button).closest('.form-group').find('input')
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
    //var count = widget.find('.form-group').length
    var fields = widget.find('.multi-fields').first()
    var firstgroup = widget.find('.form-group').first()
    
    if (firstgroup.is(':visible')) {
      var clone = fields.find('.form-group').first().clone()
      var button = clone.find('.remove-field').first()
      button.prop('disabled', false)
      button.click(function() {
        remove_field(this)
      })

      var inputbox = clone.find('input')
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
    var widget = $(button).closest('.multi-widget')
    widget.find('.remove-field').each(function() {
      remove_field(this)
    })
  }


  $('.add-field').click(function() {
    add_field(this);
  })

  $('.remove-field').click(function() {
    remove_field(this);
  })

  $('.remove-all').click(function() {
    remove_all(this);
  })

})
