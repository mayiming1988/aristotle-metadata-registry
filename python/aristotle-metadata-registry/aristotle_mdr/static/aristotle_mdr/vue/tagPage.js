var switchEditComponent = {
  template: '<div id="switch-{{ name }}">\
  <label>Description</label>\
  <template v-if="!editing">\
    {{ value }}\
  </template>\
  <template v-else>\
    <textarea name="{{ name }}" @input="textInput">{{ value }}</textarea>\
  </template>\
  <a class="inline-action" @click="toggleEdit">[Edit]</a>\
  </div>',
  props: ['name', 'value', 'initial'], 
  created: function() {
    this.value = this.initial
    this.$emit('input', this.value)
  },
  data: function() {
    return {
      editing: false
    }
  },
  methods: {
    toggleEdit: function() {
      this.editing = !this.editing
    },
    textInput: function(e) {
      this.$emit('input', e.target.value)
    }
  }
}

var vm = new Vue({
  el: '#vue-managed-content',
  components: {
    'switch-edit': switchEditComponent
  },
  data: {
    description: ''
  }
})
