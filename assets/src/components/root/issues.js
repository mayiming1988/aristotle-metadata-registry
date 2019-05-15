import comment from '@/comment.vue'
import openClose from '@/openClose.vue'
import switchEditApi from '@/switchEditApi.vue'
import inlineEdit from '@/inlineEdit.vue'
import issueComment from '@/issues/issueComment.vue'
import issueModal from '@/issues/issueModal.vue'
import issuePanel from '@/issues/issuePanel.vue'

export default {
    el: '#vue-container',
    components: {
        comment,
        issueComment,
        openClose,
        switchEditApi,
        inlineEdit,
        issueModal,
        issuePanel
    },
    data: {
        new_comments: [],
        isOpen: true,
        issueModalOpen: false
    },
    methods: {
        setIsOpen: function(isopen) {
            this.isOpen = isopen
        },
        addComment: function(comment) {
            this.new_comments.push(comment)
        },
        openIssueModal: function() {
            this.issueModalOpen = true
        }
    }
}
