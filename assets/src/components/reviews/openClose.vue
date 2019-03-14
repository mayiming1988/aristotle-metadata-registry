<template>
  <div v-bind:class="'small-alert alert-'+alertClass" role="alert">
    <strong>
      <i v-bind:class="'fa fa-'+iconClass"></i>
    </strong>
    {{ alertText }}
  </div>
</template>

<script>
export default {
    props: ['reviewStatus','initialStatus'],
    computed: {
        current_status: function() {
            return this.reviewStatus || this.initialStatus
        },
        iconClass: function () {
            switch(this.current_status) {
                case "open":
                    return "certificate"
                case "revoked":
                    return "exclamation-circle"
                case "approved":
                    return "check"
                case "closed":
                    return "certificate"
            }
            return ""
        },
        alertClass: function() {
            switch(this.current_status) {
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
            switch(this.current_status) {
                case "open":
                    return "Open"
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
.small-alert {
    border-radius: 4px;
    padding: 5px;
    display: inline-block;
    font-size: 18px;
}
</style>
