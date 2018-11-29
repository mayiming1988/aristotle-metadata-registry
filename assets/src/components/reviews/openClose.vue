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
    props: ['reviewStatus'],
    computed: {
        iconClass: function () {
            switch(this.reviewStatus) {
                case "open":
                    return "certificate"
                case "revoked":
                    return "exclamation-circle"
                case "approved":
                    return "check"
                case "closed":
                    return "certificate"
            }
        },
        alertClass: function() {
            switch(this.reviewStatus) {
                case "open":
                    return "info"
                case "revoked":
                    return "warning"
                case "approved":
                    return "success"
                case "closed":
                    return "danger"
            }
        },
        alertText: function() {
            switch(this.reviewStatus) {
                case "open":
                    return "Open"
                case "revoked":
                    return "Revoked"
                case "approved":
                    return "Approved"
                case "closed":
                    return "Closed"
            }
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
