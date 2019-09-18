<template>
  <div class="row timeline">
    <div class="col-xs-2">
    </div>
    <div class="col-sm-7 timeline-item">
        <div v-bind:class="'changedetails '+status">
            <i v-bind:class="'fa fa-fw fa-'+iconClass"></i>
            {{name}}
            {{alertText}} this review.
            <small>{{displayCreated}}</small>
        </div>
        <hr>
    </div>
  </div>
</template>

<script>
import moment from 'moment'

export default {
    props: ['name', 'status', 'created'],
    computed: {
        displayCreated: function() {
            return moment(this.created).format('Do MMM YYYY, hh:mm A')
        },
        iconClass: function () {
            switch(this.status) {
                case "open":
                    return "certificate"
                case "revoked":
                    return "exclamation-circle"
                case "approved":
                    return "check"
                case "closed":
                    return "times-circle"
            }
            return ""
        },
        divClass: function() {
            switch(this.status) {
                case "open":
                    return "info"
                case "revoked":
                    return "warning"
                case "approved":
                    return "success"
                case "closed":
                    return "danger"
            }
            return "warning"
        },
        alertText: function() {
            switch(this.status) {
                case "open":
                    return "Reopened"
                case "revoked":
                    return "Revoked"
                case "approved":
                    return "Approved"
                case "closed":
                    return "Closed"
            }
            return "Error"
        }
    }
}
</script>

<style>
.timeline-item {
    border-left: 2px solid gray;
    padding-top:10px;
    margin-top:-15px;
}
.changedetails i {
    padding-right: 10px;
    font-size:25px;
}
.changedetails.closed i {
    color:crimson;
}
.changedetails.approved i {
    color:forestgreen;
}
.changedetails.open i {
    color:cornflowerblue;
}
.small-alert {
    border-radius: 4px;
    padding: 5px;
    display: inline-block;
    font-size: 18px;
}
</style>
