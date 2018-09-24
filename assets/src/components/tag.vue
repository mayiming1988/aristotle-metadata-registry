<template>
  <div id="taggle-editor" class="input taggle_textarea"></div>
</template>

<script>
import Taggle from 'taggle'

export default {
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
</script>
