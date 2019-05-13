<template>
  <collapse-panel :title="title">
    <slot />
    <button v-if="canApprove" class="btn btn-success" @click="approve">
        Approve Changes & Close
    </button>
  </collapse-panel>
</template>

<script>
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
    methods: {
        approve: function() {
            console.log('approved')
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
