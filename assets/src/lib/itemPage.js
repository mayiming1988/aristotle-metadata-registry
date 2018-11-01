import init, { initWidgets } from '../lib/init.js'
import { initChangeStatus } from '../lib/changeStatus.js'
import favouriteComponent from '../components/favourite.vue'
import simpleList from '../components/simpleList.vue'
import tagsModal from '../components/tagsModal.vue'
import linksDisplay from '../components/linksDisplay.vue'

import Vue from 'vue'

import '../styles/aristotle.autocomplete.css'
import '../styles/aristotle.wizard.less'
import '../styles/aristotle_search.less'

export function initItemPage() {
  init()

  $(document).ready(function() {
    $('.modal').on('loaded.bs.modal', function() {
      initChangeStatus()
      initWidgets()
    })
  })

  var vm = new Vue({
    el: '#vue-container',
    components: {
      'simple-list': simpleList,
      'favourite': favouriteComponent,
      'tags-modal': tagsModal,
      'links-display': linksDisplay
    },
    data: {
      saved_tags: [],
      modalOpen: false
    },
    methods: {
      openModal: function() {
        this.modalOpen = true
      },
      closeModal: function() {
        this.modalOpen = false
      },
      updateTags: function(tags) {
        this.saved_tags = tags
        this.modalOpen = false
      }
    }
  })
}
