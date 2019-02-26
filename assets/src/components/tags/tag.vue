<template>
  <div id="taggle-editor" class="input taggle_textarea"></div>
</template>

<script>
import Taggle from 'taggle'

export default {
    props: {
        'tags': {
            type: Array,
            required: true
        },
        'newtags': {
            type: Array,
            required: true
        }
    },
    mounted: function() {
        this.tag_editor = new Taggle('taggle-editor', {
            preserveCase: true,
            tags: this.tags,
            onTagAdd: () => {
                this.updateTags()
            },
            onTagRemove: () => {
                this.updateTags()
            },
            saveOnBlur: true
        })

        // Attach events, used by autocomplete
        let input = this.tag_editor.getInput()
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
            let current_tags = this.tag_editor.getTagValues()
            for (let i=0; i < this.tags.length; i++) {
                let tag = this.tags[i]
                // Add tag if not already present
                if (current_tags.indexOf(tag == -1)) {
                    this.tag_editor.add(tag)
                }
            }
        },
        newtags: function() {
            let elements = this.tag_editor.getTagElements()
            for (let i=0; i < elements.length; i++) {
                let element = $(elements[i])
                let text = element.find('.taggle_text').text()
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
