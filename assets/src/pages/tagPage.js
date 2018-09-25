import init from '../lib/init.js'
import switchEditComponent from '../components/switchEdit.vue'

import Vue from 'vue'

import '../styles/taggle.css'

init(false)

var vm = new Vue({
  el: '#vue-container',
  components: {
    'switch-edit': switchEditComponent
  }
})
