<template>
  <button id="tag-editor-submit" type="button" class="btn btn-primary" @click="submit_tags">Save changes</button>
</template>

<script>
import { addHeaderMessage } from 'src/lib/messages.js'
import { getCSRF } from 'src/lib/cookie.js'

export default {
    props: ['submitUrl', 'tags'],
    data: () => ({
        message: 'Tags Saved',
    }),
    methods: {
        submit_tags: function() {
            var data = {
                tags: JSON.stringify(this.tags),
                csrfmiddlewaretoken: getCSRF()
            }

            $.post(this.submitUrl, data, (rdata) => {
                console.log(rdata)
                addHeaderMessage(this.message)
                this.$emit('tags-saved', rdata['tags'])
            })
        }
    }
}
</script>
