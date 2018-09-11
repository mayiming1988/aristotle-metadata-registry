var switchEditComponent = {
  template: '<div :id="divId">\
    <div class="form-group">\
    <label :for="name">{{ capitalName }}:</label>\
      <template v-if="!editing">\
        {{ value }}\
        <a class="inline-action" @click="toggleEdit">[Edit]</a>\
      </template>\
      <template v-else>\
        <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>\
        <textarea class="form-control" :name="name" v-model="value"></textarea>\
      </template>\
    </div>\
    <button v-if="editing" class="btn btn-primary" type="submit" @click="submitInput">Submit</button>\
  </div>',
  props: ['name', 'initial', 'submitUrl'], 
  created: function() {
    this.value = this.initial
    this.$emit('input', this.value)
  },
  data: function() {
    return {
      editing: false,
      value: '',
      error: ''
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
    submitInput: function(e) {
      console.log(this.submitUrl)
      var component = this
      var data = {
        csrfmiddlewaretoken: getCookie('csrftoken')
      }
      data[this.name] = this.value
      $.post(
        this.submitUrl,
        data,
        function(data) {
          if (data.success) {
            component.editing = false
          } else {
            if (data.errors[component.name] != undefined) {
              component.error = data.errors[component.name]
            } else {
              component.error = 'Field could not be updated'
            }
          }
        }
      )
    }
  }
}

var vm = new Vue({
  el: '#vue-managed-content',
  components: {
    'switch-edit': switchEditComponent
  }
})
