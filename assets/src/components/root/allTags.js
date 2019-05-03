import yesNoModal from '@/yesNoModal.vue'
import deleteButton from '@/deleteButton.vue'
import apiRequest from 'src/mixins/apiRequest.js' 
import apiErrors from '@/apiErrorDisplay.vue'

export default {
    el: '#vue-container',
    mixins: [apiRequest],
    components: {
        'yesno-modal': yesNoModal,
        'delete-button': deleteButton,
        'api-errors': apiErrors
    },
    data: {
        modal_text: 'Are you sure',
        modal_visible: false,
        tag_item: null,
    },
    methods: {
        deleteClicked: function(item) {
            this.tag_item = item
            this.modal_text = 'Are you sure you want to delete ' + item.name
            this.modal_visible = true
        },
        deleteConfirmed: function() {
            this.delete(this.tag_item['url'])
            .then(() => {
                $(this.tag_item.target).closest('tr').remove()
                this.modal_visible = false
            })
        },
        deleteCancelled: function() {
            this.modal_visible = false
        }
    }
}
