import init from '../lib/init.js'
import { initChangeStatus } from '../lib/changeStatus.js'
import { initDAL } from '../lib/dal_simple_init.js'
import Vue from 'vue'
import autocompleteTag from '../components/autocompleteTag.vue'
import favouriteComponent from '../components/favourite.vue'
import simpleList from '../components/simpleList.vue'
import submitTags from '../components/submitTags.vue'

import '../styles/aristotle.autocomplete.css'
import '../styles/aristotle.wizard.less'
import '../styles/aristotle_search.less'

export function initItemPage() {
  init(true)

  $(document).ready(function() {
    $('#infobox_adv_edit').on('loaded.bs.modal', function() {
      initChangeStatus()
      initDAL()
    })
  })

  var vm = new Vue({
    el: '#vue-container',
    components: {
      'autocomplete-tags': autocompleteTag,
      'simple-list': simpleList,
      'submit-tags': submitTags,
      'favourite': favouriteComponent
    },
    data: {
      saved_tags: [],
      current_tags: [],
      selected: '',
    },
    created: function() {
      var json = $('#tags-json').text()
      if (json != "") {
        var tags = JSON.parse(json)
      } else {
        var tags = {
          item: [],
          user: []
        }
      }
      // Tags that have been submitted (deepcopy)
      this.saved_tags = tags.item.slice()
      // Tags currently in editor
      this.current_tags = tags.item

      // All a users tags
      this.user_tags = tags.user
    },
    methods: {
      update_tags: function(tags) {
        this.current_tags = tags
      },
      update_saved_tags: function(tags) {
        this.saved_tags = tags
      },
    }
  })
}
