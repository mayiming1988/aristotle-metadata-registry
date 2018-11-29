<template>
  <div :class="alertClass" role="alert">
    <strong>
      <i class="fa fa-exclamation-circle"></i>
    </strong>
    {{ alertText }}
  </div>
</template>

<script>
export default {
    props: ['isOpen'],
    computed: {
        alertClass: function() {
            let text = 'small-alert alert-'
            if (this.isOpen) {
                text += 'success'
            } else {
                text += 'danger'
            }
            return text
        },
        alertText: function() {
            if (this.isOpen) {
                return 'Open'
            } else {
                return 'Closed'
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
