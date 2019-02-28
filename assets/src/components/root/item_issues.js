import issueModal from '@/issueModal.vue'

export default {
    el: '#vue-container',
    components: {
        'issue-modal': issueModal,
    },
    data: {
        issueModalOpen: false,
    },
    methods: {
        openIssuesModal: function() {
            this.issueModalOpen = true
        },
        closeIssuesModal: function() {
            this.issueModalOpen = false
        }
    }
}
