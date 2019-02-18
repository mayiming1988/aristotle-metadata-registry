<template>
  <div id="taggle-editor" class="input taggle_textarea"></div>
</template>

<script>
import Taggle from 'taggle'

export default {
    props: ['tags', 'newtags'],
    mounted: function() {
        this.tag_editor = new Taggle('taggle-editor', {
            preserveCase: true,
            tags: this.tags,
            onTagAdd: () => {
                this.updateTags()
            },
            onTagRemove: () => {
                this.updateTags()
            }
        })

        // Attach events, used by autocomplete
        var input = this.tag_editor.getInput()
        input.addEventListener('input', (e) => {
            this.$emit('input', e)
        })

        input.addEventListener('focus', (e) => {
            this.$emit('focus', e)
            this.$emit('input', '')
        })

        input.addEventListener('blur', (e) => {
            // If related target not set or clicking on non button element
            if (e.relatedTarget == null || e.relatedTarget.tagName != 'BUTTON') {
                this.$emit('blur', e)
            }
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
@import '../../styles/taggle.css';
</style>
