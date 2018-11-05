import { initCore } from '../lib/init.js'
import yesNoModal from '../components/yesNoModal.vue'
import deleteButton from '../components/deleteButton.vue'
import errorAlert from '../components/errorAlert.vue'
import { getCSRF } from '../lib/cookie.js'

import Vue from 'vue'

import '../styles/aristotle.dashboard.less'

initCore()

// Export root component for testing
export var rootComponent = {
    el: '#vue-container',
    components: {
        'yesno-modal': yesNoModal,
        'delete-button': deleteButton,
        'error-alert': errorAlert
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
                csrfmiddlewaretoken: getCSRF()
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
}

new Vue(rootComponent)
