$(document).ready(function() {

  $('form').each(function() {
    // Get first submit button (there should only be one)
    var form = $(this)
    var url = form.attr('action')
    if (url == undefined) {
      url = window.location.href
    }
    form.submit(function(e) {
      // Stop standard form submission
      e.preventDefault()

      var data = $(this).serialize()
      var currentform = $(this)
      $.post(
        url,
        data,
        function(data) {
          // Delete any current errors
          $('.ajax-error').remove()

          // Go through error keys
          var keys = Object.keys(data)
          for (var i = 0; i < keys.length; i++) {
            var key = keys[i]
            // get error array
            var errors = data[key]

            // Find matching field
            var field = currentform.find('input[name=' + key + ']').first()
            if (field.length == 0) {
              // Try gettings field-0 instead
              field = currentform.find('input[name=' + key + '-0]').first()
            }

            // If field was found
            if (field.length !=  0) {
              var container = field.closest('.field-container')
              var label = container.find('label').first()
              var ul = $('<ul>', {class: 'alert alert-danger ajax-error'})
              for (var j = 0; j < errors.length; j++) {
                var li = $('<li>', {text: errors[j]})
                ul.append(li)
              }
              ul.insertAfter(label)
            }
          }
        }
      )
    })
  })

})
