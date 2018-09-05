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

var tagComponent = Vue.component('taggle-tags', {
  template: '<div id="taggle-editor" class="input taggle_textarea"></div>',
  props: ['value'],
  mounted: function() {
    this.tag_modal = $('#TagEditorModal')
    this.tag_editor = new Taggle('taggle-editor', {
      preserveCase: true,
      tags: this.value,
      onTagAdd: this.tagChange,
      onTagRemove: this.tagChange
    })
    $('#tag-editor-submit').click(this.submit)
  },
  methods: {
    submit: function() {
      var tags = this.tag_editor.getTags().values
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

      this.tag_modal.modal('hide')
    },
    tagChange: function(event, tag) {
      this.tags = this.tag_editor.getTags().values
      console.log(this.tags)
      this.$emit('input', this.tags)
    }
  }
})

var vm = new Vue({
  el: '#vue-managed-content',
  data: {
    tags: []
  },
  created: function() {
    this.tags = JSON.parse($('#tags-json').text())
  }
})
