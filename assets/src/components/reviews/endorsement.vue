<template>
  <div class="row timeline">
    <div class="col-xs-2 h3">
        <span class="label label-default pull-right">
        {{registrationState}}
        </span>
    </div>
    <div class="col-sm-7 timeline-item">
        <div v-bind:class="'changedetails '+status">
            <i class="fa fa-fw fa-dot-circle-o"></i>
            {{name}} registered items for this review as 
            {{registrationState}}.
            <small>{{displayCreated}}</small>
        </div>
        <hr>
    </div>
  </div>
</template>

<script>
import moment from 'moment'

export default {
    props: ['name', 'registrationState', 'created'],
    computed: {
        displayCreated: function() {
            return moment(this.created).format('Do MMM YYYY, hh:mm A')
        },
    }
}
</script>

<style>
.timeline .h3,
.timeline-item {
    padding-top:10px;
    margin-top:-15px;
}
.timeline-item {
    border-left: 2px solid gray;
}
</style>
