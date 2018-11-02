<template>
  <modal v-model="open" title="Tag Editor" @hide="emitClose">
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
import autocompleteTag from '../components/autocompleteTag.vue'
import submitTags from '../components/submitTags.vue'

export default {
    components: {
        'modal': Modal,
        'autocomplete-tags': autocompleteTag,
        'submit-tags': submitTags
    },
    data: () => ({
        saved_tags: [],
        current_tags: [],
        user_tags: [],
        selected: '',
    }),
    props: ['itemTags', 'userTags', 'submitUrl', 'open'],
    created: function() {
        this.saved_tags = JSON.parse(this.itemTags)
        this.current_tags = this.saved_tags.slice()
        this.user_tags = JSON.parse(this.userTags)
        this.$emit('saved-tags', this.saved_tags)
    },
    methods: {
        update_tags: function(tags) {
            this.current_tags = tags
        },
        update_saved_tags: function(tags) {
            this.saved_tags = tags

            for (let tag of tags) {
                if (!this.user_tags.includes(tag)) {
                    this.user_tags.push(tag)
                }
            }

            this.$emit('saved-tags', this.saved_tags)
        },
        emitClose: function() {
            this.$emit('hide')
        }
    }
}
</script>
