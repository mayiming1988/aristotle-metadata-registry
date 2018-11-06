import { initCore } from '../lib/init.js'
import comment from '../components/comment.vue'
import issueComment from '../components/issueComment.vue'

import Vue from 'vue'

initCore()

export var rootComponent = {
    el: '#vue-container',
    components: {
        comment,
        issueComment
    },
    data: {
        new_comments: []
    }
}

new Vue(rootComponent)
