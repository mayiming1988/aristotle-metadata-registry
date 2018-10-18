var yesNoModalComponent = {
  template: '<div :id="id" class="modal fade exclude-scrap" tabindex="-1" role="dialog">\
    <div class="modal-dialog" role="document">\
      <div class="modal-content">\
        <div class="modal-header">\
          <button type="button" class="close" @click="noAction" aria-label="Close"><span aria-hidden="true">&times;</span></button>\
          <h4 class="modal-title">{{ title }}</h4>\
        </div>\
        <div class="modal-body">\
          <p>{{ text }}</p>\
        </div>\
        <div class="modal-footer">\
          <button type="button" class="btn btn-default" @click="noAction">Cancel</button>\
          <button type="button" class="btn btn-primary" @click="yesAction">Confirm</button>\
        </div>\
      </div>\
    </div>\
  </div>',
  props: ['id', 'title', 'text', 'visible'],
  methods: {
    yesAction: function() {
      this.$emit('yes')
    },
    noAction: function() {
      this.$emit('no')
    }
  },
  watch: {
    visible: function(value) {
      if (value == true) {
        $('#' + this.id).modal('show')
      } else {
        $('#' + this.id).modal('hide')
      }
    }
  }
}

var deleteButtonComponent = {
  template: '<button class="btn btn-danger" @click="deleteClicked">Delete</button>',
  props: ['itemName', 'itemId'],
  methods: {
    deleteClicked: function(e) {
      var item = {
        id: this.itemId,
        name: this.itemName,
        target: e.target
      }
      this.$emit('click', item)
    }
  }
}

var errorAlertComponent = {
  template: '<div v-if="error.length > 0" class="alert alert-danger">{{ error }}</div>',
  props: ['error']
}

var vm = new Vue({
  el: '#vue-container',
  components: {
    'yesno-modal': yesNoModalComponent,
    'delete-button': deleteButtonComponent,
    'error-alert': errorAlertComponent
  },
  data: {
    modal_text: 'Are you sure',
    modal_visible: false,
    tag_item: null,
    error_msg: ''
  },
  methods: {
    deleteClicked: function(item) {
      this.tag_item = item
      this.modal_text = 'Are you sure you want to delete ' + item.name
      this.modal_visible = true
    },
    deleteConfirmed: function() {
      var data = {
        tagid: this.tag_item.id,
        csrfmiddlewaretoken: getCookie('csrftoken')
      }
      var component = this;
      
      $.post(
        '/favourites/tagDelete',
        data,
        function(data) {
          if (data.success) {
            $(component.tag_item.target).closest('tr').remove()
          } else {
            component.error_msg = data.message
          }
          component.modal_visible = false
        }
      )
    },
    deleteCancelled: function() {
      this.modal_visible = false
    }
  }
})
