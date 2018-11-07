import { initCore } from '../lib/init.js'

import Vue from 'vue'

import comment from '../components/comment.vue'
import issueComment from '../components/issueComment.vue'
import openClose from '../components/openClose.vue'
import switchEditApi from '../components/switchEditApi.vue'

initCore()

export var rootComponent = {
    el: '#vue-container',
    components: {
        comment,
        issueComment,
        openClose,
        switchEditApi
    },
    data: {
        new_comments: [],
        isOpen: true
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

new Vue(rootComponent)
