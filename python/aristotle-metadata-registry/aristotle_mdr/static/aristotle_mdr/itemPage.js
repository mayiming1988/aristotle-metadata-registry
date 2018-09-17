favouriteComponent = {
  template: '<a class="btn btn-default favourite" :title="linkTitle" @click="submitFavourite">\
    <i :class="iconClass"></i>\
  </a>',
  props: ['initial', 'submitUrl'],
  data: function() {
    return {
      onIcon: 'fa fa-bookmark',
      favourited: false
    }
  },
  created: function() {
    if (this.initial == 'True') {
      this.favourited = true
    } else {
      this.favourited = false
    }
  },
  computed: {
    linkTitle: function() {
      if (this.favourited) {
        return 'Add to my favourites'
      } else {
        return 'Remove from my favourites'
      }
    },
    iconClass: function() {
      if (this.favourited) {
        return this.onIcon
      } else {
        return this.onIcon + '-o'
      }
    }
  },
  methods: {
    submitFavourite: function(e) {
      var component = this
      $.get(
        this.submitUrl,
        function(data) {
          component.favourited = data.favourited
          addHeaderMessage(data.message)
        }
      )
    }
  }
}

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
      var current_tags = this.tag_editor.getTagValues()
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

var submitTags = {
  template: '<button id="tag-editor-submit" type="button" class="btn btn-primary" @click="submit_tags">Save changes</button>',
  props: ['submitUrl', 'tags', 'modal'],
  methods: {
    submit_tags: function() {
      var csrf_token = getCookie('csrftoken')
      var url = this.submitUrl
      var tags = this.tags
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

      this.$emit('tags-saved', tags)
      $(this.modal).modal('hide')
    },
  }
}

var vm = new Vue({
  el: '#vue-container',
  components: {
    'taggle-tags': tagComponent,
    'simple-list': simpleList,
    'submit-tags': submitTags,
    'favourite': favouriteComponent
  },
  data: {
    saved_tags: [],
    current_tags: [],
    selected: '',
  },
  created: function() {
    var json = $('#tags-json').text()
    if (json != "") {
      var tags = JSON.parse(json)
    } else {
      var tags = {
        item: [],
        user: []
      }
    }
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
    update_tags: function(tags) {
      this.current_tags = tags
    },
    update_saved_tags: function(tags) {
      this.saved_tags = tags
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
