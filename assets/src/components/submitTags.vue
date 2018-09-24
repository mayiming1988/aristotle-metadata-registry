<template>
  <button id="tag-editor-submit" type="button" class="btn btn-primary" @click="submit_tags">Save changes</button>
</template>

<script>
import { getCSRF } from '../lib/cookie.js'
import { addHeaderMessage } from '../lib/messages.js'

export default {
  props: ['submitUrl', 'tags', 'modal'],
  methods: {
    submit_tags: function() {
      var csrf_token = getCSRF()
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
</script>
