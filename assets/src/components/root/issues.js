import comment from '@/comment.vue'
import openClose from '@/openClose.vue'
import switchEditApi from '@/switchEditApi.vue'
import inlineEdit from '@/inlineEdit.vue'
import issueComment from '@/issues/issueComment.vue'
import issueModal from '@/issues/issueModal.vue'
import issuePanel from '@/issues/issuePanel.vue'

import 'src/styles/taggle.css'

export default {
    el: '#vue-container',
    components: {
        'comment': comment,
        'issue-comment': issueComment,
        'open-close': openClose,
        'switch-edit-api': switchEditApi,
        'inline-edit': inlineEdit,
        'issue-modal': issueModal,
        'issue-panel': issuePanel,
    },
    data: function() {
        let data = {
            new_comments: [],
            issueModalOpen: false,
        }
        // Get isopen from json element
        let issue_data = JSON.parse(document.getElementById("issue-data").textContent)
        data.isOpen = issue_data.isopen

        return data
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
