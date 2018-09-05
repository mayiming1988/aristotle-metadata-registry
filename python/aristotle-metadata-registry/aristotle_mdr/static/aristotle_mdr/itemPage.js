$(document).ready(function() {

  var tag_modal = $('#TagEditorModal')
  var current_tags = JSON.parse($('#tags-json').text())
  var tag_editor = new Taggle('taggle-editor', {
    preserveCase: true,
    tags: current_tags
  });

  $('#tag-editor-submit').click(function() {
    var tags = tag_editor.getTags().values
    var csrf_token = getCookie('csrftoken')
    var url = edit_tag_url
    var data = {
      tags: JSON.stringify(tags),
      csrfmiddlewaretoken: csrf_token
    }

    $.post(
      url,
      data,
      function(data) {
        console.log(data)
      }
    )

    tag_modal.modal('hide')

  })

  // Async favouriting
  var fav_button = $('.btn.favourite').first()
  var fav_url = fav_button.attr('href')
  fav_button.removeAttr('href')

  fav_button.click(function() {
    $.get(
      fav_url,
      function(data) {
        console.log(data)
        var i = fav_button.find('i').first()
        if (data.favourited) {
          i.removeClass('fa-bookmark-o').addClass('fa-bookmark')
        } else {
          i.removeClass('fa-bookmark').addClass('fa-bookmark-o')
        }
      }
    )
  })

})
