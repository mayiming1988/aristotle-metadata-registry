<template>
  <modal :value="open" @input="emitClose" title="Tag Editor" @hide="emitClose">
    <p>Update your tags for this item, new tags (shown darker) will be created for you</p>

    <autocomplete-tags :current_tags="current_tags" :user_tags="user_tags" @tag-update="update_tags"></autocomplete-tags>
    <div slot="footer">
      <button type="button" class="btn btn-default" @click="emitClose">Close</button>
      <submit-tags 
        :submit-url="submitUrl"
        :tags="current_tags"
        @tags-saved="update_saved_tags">
      </submit-tags>
    </div>
  </modal>
</template>

<script>
import { Modal } from 'uiv'
import autocompleteTag from '@/tags/autocompleteTag.vue'
import submitTags from '@/tags/submitTags.vue'
import { flatten } from 'src/lib/utils.js'

export default {
    components: {
        'modal': Modal,
        'autocomplete-tags': autocompleteTag,
        'submit-tags': submitTags
    },
    data: () => ({
        current_tags: [],
        user_tags: [],
        selected: '',
    }),
    props: ['itemTags', 'userTags', 'submitUrl', 'open'],
    created: function() {
        let saved_tags = JSON.parse(this.itemTags)
        this.current_tags = saved_tags.slice() // Deep copy
        this.user_tags = JSON.parse(this.userTags)
        this.$emit('saved-tags', saved_tags)
    },
    methods: {
        update_tags: function(tags) {
            this.current_tags = tags
        },
        update_saved_tags: function(tags) {
            for (let tag of tags) {
                if (!this.user_tags.includes(tag)) {
                    this.user_tags.push(tag)
                }
            }

            this.$emit('saved-tags', tags)
        },
        emitClose: function() {
            this.$emit('hide')
        }
    }
}
</script>
