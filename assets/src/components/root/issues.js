import comment from '@/comment.vue'
import issueComment from '@/issueComment.vue'
import openClose from '@/openClose.vue'
import switchEditApi from '@/switchEditApi.vue'
import inlineEdit from '@/inlineEdit.vue'
import issueModal from '@/issueModal.vue'

export default {
    el: '#vue-container',
    components: {
        comment,
        issueComment,
        openClose,
        switchEditApi,
        inlineEdit,
        issueModal
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
        }
    }
}
