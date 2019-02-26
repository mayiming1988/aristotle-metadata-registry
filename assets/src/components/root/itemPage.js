import favouriteComponent from '@/favourite.vue'
import simpleLinkList from '@/simpleLinkList.vue'
import tagsModal from '@/tags/tagsModal.vue'
import linksDisplay from '@/linksDisplay.vue'

export default {
    el: '#vue-container',
    components: {
        'simple-linked-list': simpleLinkList,
        'favourite': favouriteComponent,
        'tags-modal': tagsModal,
        'links-display': linksDisplay,
    },
    data: {
        saved_tags: [],
        tagsModalOpen: false,
        issueModalOpen: false,
    },
    methods: {
        openTagsModal: function() {
            this.tagsModalOpen = true
        },
        closeTagsModal: function() {
            this.tagsModalOpen = false
        },
        updateTags: function(tags) {
            this.saved_tags = tags
            this.tagsModalOpen = false
        }
    },
    computed: {
        hasTags: function() {
            return this.saved_tags.length > 0
        }
    }
}
