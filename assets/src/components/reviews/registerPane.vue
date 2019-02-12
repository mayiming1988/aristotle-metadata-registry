<template>
  <div class="row" v-if="isOpen">
    <div class="col-sm-8 col-sm-offset-1" >
      <hr>
      <div class="panel panel-success">
        <div class="panel-heading">
          <div class="panel-title">Approve and endorse metadata</div>
        </div>
        <div class="panel-body">
          <p>
            Approve this review request to endorse the attached metadata as
            <em>{{targetRegistrationState}}</em> in the registration authority
            <a :href="registrationAuthorityUrl">{{registrationAuthority }}</a>
          </p>
        </div>
        <div class="panel-footer clearfix">
          <a v-if="targetRegistrationState !== 'None'" :href="approvalUrl" class="btn btn-success">Approve as <em>{{targetRegistrationState}}</em> and Close</a>
          <a :href="endorseUrl" class="btn btn-default">Endorse with a different status</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import apiRequest from 'src/mixins/apiRequest.js'

export default {
    mixins: [apiRequest],
    props: [
        'reviewStatus','initialStatus',
        'registrationAuthority', 'registrationAuthorityUrl',
        'targetRegistrationState',
        'approvalUrl', 'endorseUrl'
    ],
    data: () => ({
    }),
    created: function() {
        // this.current_state = this.initialReviewState
    },
    methods: {
    },
    computed: {
        current_status: function() {
            return this.reviewStatus || this.initialStatus
        },
        isOpen: function() {
            return this.current_status == 'open'
        },
        canOpenClose: function() {
            return (this.openClosePermission == 'True')
        },
    }
}
</script>

<style>
.text-right {
    text-align: "right"
}
</style>
