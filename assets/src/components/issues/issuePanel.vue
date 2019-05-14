<template>
  <div class="issuePanel">
      <!-- Colapsable panel -->
      <collapse-panel :title="title">
        <slot />
        <button v-if="canApprove" class="btn btn-success" @click="openConfirmDialog">
            Approve Changes & Close
        </button>
      </collapse-panel>
      <!-- Confirm modal -->
      <confirm-modal :visible="confirmOpen" :text="confirmMessage" @yes="approve" @no="closeConfirmDialog" />
  </div>
</template>

<script>
import { addHeaderMessage } from 'src/lib/messages.js'
import apiRequest from 'src/mixins/apiRequest.js'
import collapsePanel from '@/collapsePanel.vue'
import Modal from 'uiv/src/components/modal/Modal.vue'
import confirmModal from '@/yesNoModal.vue'

export default {
    mixins: [apiRequest],
    components: {
        'collapse-panel': collapsePanel,
        'confirm-modal': confirmModal
    },
    props: {
        fieldName: {
            type: String,
            required: true
        },
        canApprove: {
            type: Boolean,
            default: false
        },
        approveUrl: {
            type: String,
            required: true
        }
    },
    data: () => ({
        message: 'Changes applied',
        confirmMessage: 'Are you sure you want to approve these changes?',
        confirmOpen: false
    }),
    methods: {
        approve: function() {
            let data = {
                'isopen': false
            }

            let promise = this.post(this.approveUrl, data)
            promise.then((response) => {
                if (response.status == 200) {
                    addHeaderMessage(this.message)
                    this.$emit('set_open', false)
                }
            })
        },
        openConfirmDialog: function() {
            this.confirmOpen = true
        },
        closeConfirmDialog: function() {
            this.confirmOpen = false
        }
    },
    computed: {
        title: function() {
            return 'Proposed changes to ' + this.fieldName
        }
    }
}
</script>

<style>
a.blackLink {
    color: #333333;
}
</style>
