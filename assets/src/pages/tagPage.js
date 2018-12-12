import { initCore } from '../lib/init.js'
import switchEditComponent from '../components/switchEdit.vue'

import Vue from 'vue'

import '../styles/taggle.css'
import '../styles/aristotle.dashboard.less'

initCore()

// Export root component for testing
export var rootComponent = {
    el: '#vue-container',
    components: {
        'switch-edit': switchEditComponent
    }
}

new Vue(rootComponent)
