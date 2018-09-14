var yesNoModalComponent = {
  template: '<div :id="id" class="modal fade exclude-scrap" tabindex="-1" role="dialog">\
    <div class="modal-dialog" role="document">\
      <div class="modal-content">\
        <div class="modal-header">\
          <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>\
          <h4 class="modal-title">{{ title }}</h4>\
        </div>\
        <div class="modal-body">\
          <p>{{ text }}</p>\
        </div>\
        <div class="modal-footer">\
          <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>\
          <button type="button" class="btn btn-primary" @click="yesAction">Confirm</button>\
        </div>\
      </div>\
    </div>\
  </div>',
  props: ['id', 'title', 'text'],
  methods: {
    yesAction: function() {
      this.$emit('yes')
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

var vm = new Vue({
  el: '#vue-container',
  components: {
    'yesno-modal': yesNoModalComponent,
    'delete-button': deleteButtonComponent
  },
  data: {
    modal_text: 'Are you sure',
    tag_item: null
  },
  methods: {
    deleteClicked: function(item) {
      console.log(item)
      this.tag_item = item.id
      this.modal_text = 'Are you sure you want to delete ' + item.name
      $('#deleteTagModal').modal('show')
    },
    deleteConfirmed: function() {
      console.log('deleting')
      console.log(this.tag_item)
    }
  }
})
