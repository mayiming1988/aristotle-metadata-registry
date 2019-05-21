import yesNoModal from '@/yesNoModal.vue'
import deleteButton from '@/deleteButton.vue'
import apiRequest from 'src/mixins/apiRequest.js'
import apiErrors from '@/apiErrorDisplay.vue'
import openClose from '@/reviews/openClose.vue'


export default {
    el: '#vue-container',
    mixins: [apiRequest],
    components: {
        'yesno-modal': yesNoModal,
        'delete-button': deleteButton,
        'api-errors': apiErrors,
        'open-close-approved': openClose
    },
    data: {
        modal_text: '',
        modal_visible: false,
        tag_item: null,
    },
    methods: {
        deleteClicked: function(item) {
            this.item = item
            this.modal_text = item.modalText
            this.modal_visible = true
        },
        deleteConfirmed: function() {
            let data = {"concept_id": this.item.id}
            this.put(this.item['url'], data)
            .then(() => {
                $(this.item.target).closest('tr').remove()
                this.modal_visible = false
            })
        },
        deleteCancelled: function() {
            this.modal_visible = false
        }
    }
}

