import init, { initWidgets } from '../lib/init.js'
import { initChangeStatus } from '../lib/changeStatus.js'
import favouriteComponent from '../components/favourite.vue'
import simpleList from '../components/simpleList.vue'
import tagsModal from '../components/tagsModal.vue'
import linksDisplay from '../components/linksDisplay.vue'
import issueModal from '../components/issueModal.vue'

import Vue from 'vue'

import '../styles/aristotle.wizard.less'
import '../styles/aristotle_search.less'

// Export root component for testing
export var rootComponent = {
    el: '#vue-container',
    components: {
        'simple-list': simpleList,
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
    }
}

export function initItemPage() {
    init()

    $(document).ready(function() {
        $('.modal').on('loaded.bs.modal', function() {
            initChangeStatus()
            initWidgets()
        })
    })

    new Vue(rootComponent)
}
