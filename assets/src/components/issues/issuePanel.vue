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
      <modal v-model="confirmOpen" title="Confirm">
        Are you sure you want to approve these changes
        <div slot="footer">
            <button class="btn btn-default" @click="closeConformDialog">
                Cancel
            </button>
            <button class="btn btn-success" @click="approve">
                Confirm
            </button>
        </div>
      </modal>
  </div>
</template>

<script>
import { addHeaderMessage } from 'src/lib/messages.js'
import apiRequest from 'src/mixins/apiRequest.js'
import collapsePanel from '@/collapsePanel.vue'
import Modal from 'uiv/src/components/modal/Modal.vue'

export default {
    mixins: [apiRequest],
    components: {
        'collapse-panel': collapsePanel,
        'modal': Modal
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
        closeConformDialog: function() {
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
