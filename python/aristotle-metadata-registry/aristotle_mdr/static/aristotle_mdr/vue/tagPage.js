var switchEditComponent = {
  template: '<div :id="divId">\
    <div class="form-group">\
    <label :for="name">{{ capitalName }}:</label>\
      <template v-if="!editing">\
        {{ value }}\
        <a class="inline-action" @click="toggleEdit">[Edit]</a>\
      </template>\
      <template v-else>\
        <textarea class="form-control" :name="name" @input="textInput">{{ value }}</textarea>\
      </template>\
    </div>\
    <button v-if="editing" class="btn btn-primary" type="submit" @click="submitInput">Submit</button>\
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
  computed: {
    divId: function() {
      return 'switch-' + this.name
    },
    capitalName: function() {
      return this.name.slice(0,1).toUpperCase() + this.name.slice(1)
    },
  },
  methods: {
    toggleEdit: function() {
      this.editing = true
    },
    textInput: function(e) {
      this.$emit('input', e.target.value)
    },
    submitInput: function(e) {
      this.$emit('submit', e)
      this.editing = false
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
  },
})
