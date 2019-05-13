<template>
    <div class="panel panel-default">
      <div class="panel-heading">
        <strong>
          <a class="blackLink" role="button" data-toggle="collapse" href="#collapseProposal" aria-expanded="false" aria-controls="#collapseProposal">
            Proposed changes to {{ fieldName }}
          </a>
        </strong>
      </div>
      <div id="collapseProposal" class="collapse panel-body">
        <slot></slot>
        <button v-if="canApprove" class="btn btn-success" @click="approve">Approve</button>
      </div>
    </div>
</template>

<script>
import apiRequest from 'src/mixins/apiRequest.js'

export default {
    mixins: [apiRequest],
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
    }
}
</script>

<style>
a.blackLink {
    color: #333333;
}
</style>
