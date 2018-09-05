$(document).ready(function() {

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
        addHeaderMessage(data.message)
      }
    )
  })

})

Vue.component('taggle-tags', {
  template: '<div id="taggle-editor" class="input taggle_textarea"></div>',
  props: ['initial'],
  mounted: function() {
    this.tag_editor = new Taggle('taggle-editor', {
      preserveCase: true,
      tags: this.initial,
    })

    var component = this;
    $('#tag-editor-submit').click(function() {
      var tags = component.tag_editor.getTags().values
      component.$emit('submit', tags)
    })
  }
})

var vm = new Vue({
  el: '#vue-managed-content',
  data: {
    saved_tags: []
  },
  created: function() {
    this.saved_tags = JSON.parse($('#tags-json').text())
  },
  methods: {
    submit_tags: function(tags) {
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
          addHeaderMessage(data.message)
        }
      )

      this.saved_tags = tags
      $('#TagEditorModal').modal('hide')
    }
  }
})
