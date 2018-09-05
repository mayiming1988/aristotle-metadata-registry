$(document).ready(function() {

  var tag_editor = new Taggle('taggle-editor');
  var tag_modal = $('#TagEditorModal')

  $('#tag-editor-submit').click(function() {
    var tags = tag_editor.getTags().values
    var csrf_token = getCookie('csrftoken')
    console.log(csrf_token)
    var url = edit_tag_url
    console.log(url)
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
