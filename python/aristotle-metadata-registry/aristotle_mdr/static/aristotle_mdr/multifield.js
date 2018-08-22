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

  function add_field(button) {
    var widget = $(button).closest('.multi-widget')
    var fields = widget.find('.multi-fields').first()
    var clone = fields.find('.form-group').first().clone()
    var button = clone.find('.remove-field').first()
    
    button.prop('disabled', false)
    button.click(function() {
      remove_field(this)
    })

    clone.find('input').val('')
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
