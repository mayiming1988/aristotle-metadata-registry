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

tagComponent = {
  template: '<div><div id="taggle-editor" class="input taggle_textarea"></div><div id="autocomplete"></div></div>',
  props: ['initial', 'value'],
  mounted: function() {
    var component = this;

    this.tag_editor = new Taggle('taggle-editor', {
      preserveCase: true,
      tags: this.initial,
      onTagAdd: function() {
        component.$emit('input', '')
      }
    })

    $('#tag-editor-submit').click(function() {
      var tags = component.tag_editor.getTags().values
      component.$emit('submit', tags)
    })

    // Attach events, used by autocomplete
    var input = this.tag_editor.getInput()
    $(input).on('input', function(e) {
      component.$emit('input', $(e.target).val())
    })

    $(input).on('focus', function(e) {
      component.$emit('focus')
    })

    $(input).on('blur', function(e) {
      component.$emit('input', '')
      component.$emit('blur')
    })
  },
  watch: {
    value: function() {
      this.tag_editor.add(this.value)
    }
  }
}

var vm = new Vue({
  el: '#vue-managed-content',
  components: {
    'taggle-tags': tagComponent
  },
  data: {
    saved_tags: [],
    selected: '',
  },
  created: function() {
    var tags = JSON.parse($('#tags-json').text())
    this.saved_tags = tags.item
    this.user_tags = tags.user
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
    },
    getSuggestions: function() {
      return this.user_tags
    },
    makeSuggestion: function(suggestion) {
      this.selected = suggestion
    }
  }
})
