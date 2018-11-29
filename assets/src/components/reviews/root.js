import comment from '@/comment.vue'
import reviewComment from '@/reviews/reviewComment.vue'
import statusChangeTimeline from '@/reviews/statusChange.vue'
import registerPane from '@/reviews/registerPane.vue'
import endorsementTimeline from '@/reviews/endorsement.vue'
import openCloseApproved from '@/reviews/openClose.vue'
import switchEditApi from '@/switchEditApi.vue'
import inlineEdit from '@/inlineEdit.vue'
import timeline from '@/reviews/timeline.vue'

export default {
    el: '#vue-container',
    components: {
        comment,
        reviewComment,
        openCloseApproved,
        switchEditApi,
        inlineEdit,
        statusChangeTimeline,
        timeline,
        endorsementTimeline,
        registerPane
    },
    data: {
        new_comments: [],
        status: '',
        timeline_items: [],
    },
    methods: {
        setStatus: function(state) {
            this.status = state
            this.timeline_items.push({type: "status_change", data: {name: "You", status_code: state}})
        },
        addComment: function(comment) {
            // this.new_comments.push(comment)
            this.timeline_items.push({type: "comment", data: comment})
        }
    }
}
