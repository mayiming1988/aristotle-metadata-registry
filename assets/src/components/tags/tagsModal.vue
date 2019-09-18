<template>
  <modal :value="open" @input="emitClose" title="Tag Editor" @hide="emitClose">
    <p>Update your tags for this item, new tags (shown darker) will be created for you</p>
    <p>Press enter to create and separate your tags</p>

    <api-errors :errors="errors" />
    <autocomplete-tags :current_tags="current_tags" :user_tags="userTagsFlat" @tag-update="update_tags" />
    <div slot="footer">
      <button type="button" class="btn btn-default" @click="emitClose">
          Close
      </button>
      <submit-tags 
        :submit-url="submitUrl"
        :tags="current_tags"
        @error="setErrors"
        @tags-saved="update_saved_tags" 
      />
    </div>
  </modal>
</template>

<script>
import Modal from 'uiv/src/components/modal/Modal.vue'
import autocompleteTag from '@/tags/autocompleteTag.vue'
import submitTags from '@/tags/submitTags.vue'
import { flatten } from 'src/lib/utils.js'
import apiErrors from '@/apiErrorDisplay.vue'

export default {
    components: {
        'modal': Modal,
        'autocomplete-tags': autocompleteTag,
        'submit-tags': submitTags,
        'api-errors': apiErrors,
    },
    data: () => ({
        current_tags: [],
        user_tags: [],
        errors: {},
        selected: '',
    }),
    props: {
        'itemTags': {
            type: String,
            required: true
        },
        'userTags': {
            type: String,
            required: true
        },
        'submitUrl': {
            type: String,
            required: true
        },
        'open': {
            type: Boolean,
            default: false
        }
    },
    created: function() {
        let saved_tags = JSON.parse(this.itemTags)
        for (let tag of saved_tags) {
            tag['name'] = tag['tag__name']
            tag['id'] = tag['tag__id']
        }
        this.current_tags = flatten(saved_tags, 'name')
        this.user_tags = JSON.parse(this.userTags)
        this.$emit('saved-tags', saved_tags)
    },
    methods: {
        update_tags: function(tags) {
            this.current_tags = tags
        },
        update_saved_tags: function(tags) {
            for (let tag of tags) {
                if (!this.userTagsFlat.includes(tag['name'])) {
                    this.user_tags.push(tag)
                }
            }

            this.$emit('saved-tags', tags)
            this.emitClose()
        },
        emitClose: function() {
            this.$emit('hide')
        },
        setErrors: function(errors) {
            this.errors = errors
        }
    },
    computed: {
        userTagsFlat: function() {
            return flatten(this.user_tags, 'name')
        }
    }
}
</script>
