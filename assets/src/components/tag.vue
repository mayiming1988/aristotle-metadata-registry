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

<style>
.taggle_textarea {
  width: 100%;
  height: auto;
  overflow: hidden;
  border: 1px solid #ccc;
}

.taggle {
  color: #3E6D8E;
}

.taggle_list {
  float: left;
  padding: 3px;
  margin: 0;
  width: 100%;
  box-sizing: content-box;
}

.taggle_input {
  border: none;
  outline: none;
  font-size: 16px;
  font-weight: 300;
}

.taggle_list li {
  float: left;
  display: inline-block;
  white-space: nowrap;
  font-weight: 500;
  margin-bottom: 5px;
}

.taggle_list .taggle {
  font-weight: 200;
  margin-right: 8px;
  background-color: #E0EAF1;
  padding: 5px 10px;
  padding-right: 15px;
  border-radius: 0;
  position: relative;
  cursor: pointer;
  transition: all .3s;
  -webkit-animation-duration: 1s;
          animation-duration: 1s;
  -webkit-animation-fill-mode: both;
          animation-fill-mode: both;
}

.taggle_list .taggle_newtag {
  background-color: #3a6482 !important;
  color: white !important;
}

.taggle_list .taggle_postit {
  background-color: gold !important;
}

.taggle_list .taggle_hot {
  background: #BDD0DD;
}

.taggle_list .taggle .close {
  font-size: 1.5rem;
  position: absolute;
  top: 3px;
  right: 3px;
  text-decoration: none;
  padding: 0;
  line-height: .1rem;
  color: #aaa;
  border: 0;
  background: none;
  cursor: pointer;
  display: block;
  border-radius: 1.3rem;
  width: 1.3rem;
  height: 1.3rem;
  opacity: unset;
}

.taggle_list .taggle .close:hover {
  background: #C03434;
  color: #fff;
}

.taggle_placeholder {
  position: absolute;
  color: #CCC;
  /* top: 12px; */
  padding: 3px;
  left: 15px;
  transition: opacity, .25s;
  -webkit-user-select: none;
     -moz-user-select: none;
      -ms-user-select: none;
          user-select: none;
}

.taggle_input {
  padding: 8px;
  padding-left: 0;
  float: left;
  margin-top: -5px;
  background: none;
  width: 100%;
  max-width: 100%;
}

.taggle_sizer {
  padding: 0;
  margin: 0;
  position: absolute;
  top: -500px;
  z-index: -1;
  visibility: hidden;
}
</style>
