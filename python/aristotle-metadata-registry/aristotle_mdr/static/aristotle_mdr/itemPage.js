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
  template: '<div id="taggle-editor" class="input taggle_textarea"></div>',
  props: ['tags', 'newtags'],
  mounted: function() {
    var component = this;

    this.tag_editor = new Taggle('taggle-editor', {
      preserveCase: true,
      tags: component.tags,
      onTagAdd: function(e, tag) {
        component.updateTags()
      },
      onTagRemove: function(e, tag) {
        component.updateTags()
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
      component.$emit('input', $(this).val())
    })

    $(input).on('blur', function(e) {
      component.$emit('blur', e)
    })
  },
  methods: {
    updateTags: function() {
      this.$emit('tag-update', this.tag_editor.getTagValues())
    }
  },
  watch: {
    tags: function() {
      current_tags = this.tag_editor.getTagValues()
      for (var i=0; i < this.tags.length; i++) {
        var tag = this.tags[i]
        // Add tag if not already present
        if (current_tags.indexOf(tag == -1)) {
          this.tag_editor.add(tag)
        }
      }
    },
    newtags: function() {
      var elements = this.tag_editor.getTagElements()
      for (var i=0; i < elements.length; i++) {
        var element = $(elements[i])
        var text = element.find('.taggle_text').text()
        if (this.newtags.indexOf(text) != -1) {
          element.addClass('taggle_newtag')
        } else {
          element.removeClass('taggle_newtag')
        }
      }
    }
  }
}

var simpleList = {
  template: '<ul :class="ulClass">\
    <li v-for="item in data" :class="liClass">{{ item }}</li>\
  </ul>',
  props: ['ulClass', 'liClass', 'data'],
}

var vm = new Vue({
  el: '#vue-managed-content',
  components: {
    'taggle-tags': tagComponent,
    'simple-list': simpleList
  },
  data: {
    saved_tags: [],
    current_tags: [],
    selected: '',
  },
  created: function() {
    var tags = JSON.parse($('#tags-json').text())
    // Tags that have been submitted (deepcopy)
    this.saved_tags = tags.item.slice()
    // Tags currently in editor
    this.current_tags = tags.item

    // All a users tags
    this.user_tags = tags.user
  },
  computed: {
    newTags: function() {
      newTags = []
      for (var i=0; i < this.current_tags.length; i++) {
        var element = this.current_tags[i]
        if (this.user_tags.indexOf(element) == -1) {
          newTags.push(element)
        }
      }
      return newTags
    }
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
          addHeaderMessage(data.message)
        }
      )

      this.saved_tags = tags
      $('#TagEditorModal').modal('hide')
    },
    update_tags: function(tags) {
      this.current_tags = tags
    },
    getSuggestions: function() {
      suggestions = []
      for (var i=0; i < this.user_tags.length; i++) {
        var element = this.user_tags[i]
        // Add to suggestions if not in current tags
        if (this.current_tags.indexOf(element) == -1) {
          suggestions.push(element)
        }
      }
      return suggestions
    },
    makeSuggestion: function(suggestion) {
      if (suggestion != null) {
        this.current_tags.push(suggestion)
      }
    }
  }
})
