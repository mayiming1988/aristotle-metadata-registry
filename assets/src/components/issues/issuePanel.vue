<template>
  <collapse-panel :title="title">
    <slot />
    <button v-if="canApprove" class="btn btn-success" @click="approve">
        Approve Changes & Close
    </button>
  </collapse-panel>
</template>

<script>
import { addHeaderMessage } from 'src/lib/messages.js'
import apiRequest from 'src/mixins/apiRequest.js'
import collapsePanel from '@/collapsePanel.vue'

export default {
    mixins: [apiRequest],
    components: {
        'collapse-panel': collapsePanel
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
        message: 'Changes applied'
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
