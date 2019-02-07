import favouriteComponent from '@/favourite.vue'
import simpleLinkList from '@/simpleLinkList.vue'
import tagsModal from '@/tags/tagsModal.vue'
import linksDisplay from '@/linksDisplay.vue'
import issueModal from '@/issueModal.vue'

console.log(linksDisplay)

export default {
    el: '#vue-container',
    components: {
        'simple-linked-list': simpleLinkList,
        'favourite': favouriteComponent,
        'tags-modal': tagsModal,
        'links-display': linksDisplay,
        'issue-modal': issueModal
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
        openIssuesModal: function() {
            this.issueModalOpen = true
        },
        closeIssuesModal: function() {
            this.issueModalOpen = false
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
