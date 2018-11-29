import comment from '@/comment.vue'
import reviewComment from '@/reviews/reviewComment.vue'
import openCloseApproved from '@/reviews/openClose.vue'
import switchEditApi from '@/switchEditApi.vue'
import inlineEdit from '@/inlineEdit.vue'

export default {
    el: '#vue-container',
    components: {
        comment,
        reviewComment,
        openCloseApproved,
        switchEditApi,
        inlineEdit
    },
    data: {
        new_comments: [],
        status: 'open'
    },
    methods: {
        setStatus: function(state) {
            this.status = state
        },
        addComment: function(comment) {
            this.new_comments.push(comment)
        }
    }
}
