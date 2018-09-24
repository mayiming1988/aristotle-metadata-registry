<template>
  <vue-simple-suggest :list="getSuggestions" :filter-by-query="true" @select="makeSuggestion">
    <taggle-tags :tags="current_tags" :newtags="newTags" @tag-update="update_tags"></taggle-tags>
  </vue-simple-suggest>
</template>

<script>
import VueSimpleSuggest from 'vue-simple-suggest'
import tagComponent from './tag.vue'

export default {
  components: {
    'taggle-tags': tagComponent,
    'vue-simple-suggest': VueSimpleSuggest
  },
  props: ['current_tags', 'user_tags'],
  computed: {
    newTags: function() {
      var newTags = []
      for (var i=0; i < this.current_tags.length; i++) {
        var element = this.current_tags[i]
        if (this.user_tags.indexOf(element) == -1) {
          newTags.push(element)
        }
      }
      return newTags
    }
  },
  methods: {
    getSuggestions: function() {
      var suggestions = []
      for (var i=0; i < this.user_tags.length; i++) {
        var element = this.user_tags[i]
        // Add to suggestions if not in current tags
        if (this.current_tags.indexOf(element) == -1) {
          suggestions.push(element)
        }
      }
      return suggestions
    },
    makeSuggestion: function(suggestion) {
      if (suggestion != null) {
        this.current_tags.push(suggestion)
      }
    },
    update_tags: function(tags) {
      this.$emit('tag-update', tags)
    }
  }
}
</script>
