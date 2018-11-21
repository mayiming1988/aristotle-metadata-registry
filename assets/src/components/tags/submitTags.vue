<template>
  <button id="tag-editor-submit" type="button" class="btn btn-primary" @click="submit_tags">Save changes</button>
</template>

<script>
import { getCSRF } from 'src/lib/cookie.js'
import { addHeaderMessage } from 'src/lib/messages.js'
import { flatten } from 'src/lib/utils.js'

export default {
    props: ['submitUrl', 'tags'],
    methods: {
        submit_tags: function() {
            var csrf_token = getCSRF()
            var url = this.submitUrl
            var tags = this.tags
            var data = {
                tags: JSON.stringify(this.flatTags),
                csrfmiddlewaretoken: csrf_token
            }

            $.post(
                url,
                data,
                (data) => {
                    addHeaderMessage(data.message)
                    this.$emit('tags-saved', this.flatTags)
                }
            )

        },
    },
    computed: {
        flatTags: function() {
            return flatten(this.tags, 'name')
        }
    }
}
</script>
