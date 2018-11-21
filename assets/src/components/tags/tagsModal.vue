<template>
  <modal :value="open" @input="emitClose" title="Tag Editor" @hide="emitClose">
    <p>Update your tags for this item, new tags (shown darker) will be created for you</p>

    <autocomplete-tags :current_tags="currentTagsFlat" :user_tags="userTagsFlat" @tag-update="update_tags"></autocomplete-tags>
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
        saved_tags: [],
        current_tags: [],
        user_tags: [],
        selected: '',
    }),
    props: ['itemTags', 'userTags', 'submitUrl', 'open'],
    created: function() {
        this.saved_tags = JSON.parse(this.itemTags)
        for (let tag of this.saved_tags) {
            tag['name'] = tag['tag__name']
            tag['id'] = tag['tag__id']
        }
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
    },
    computed: {
        currentTagsFlat: function() {
            return flatten(this.current_tags, 'name')
        },
        userTagsFlat: function() {
            return flatten(this.user_tags, 'name')
        }
    }
}
</script>
