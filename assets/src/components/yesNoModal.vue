<template>
  <div ref="modal" class="modal fade exclude-scrap" tabindex="-1" role="dialog">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="close" @click="noAction" aria-label="Close"><span aria-hidden="true">&times;</span></button>
          <h4 class="modal-title">{{ title }}</h4>
        </div>
        <div class="modal-body">
          <p>{{ text }}</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-default" @click="noAction">Cancel</button>
          <button type="button" class="btn btn-primary" @click="yesAction">Confirm</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
    props: {
        title: {
            type: String,
            default: 'Confirm'
        },
        text: {
            type: String,
            required: true
        },
        visible: {
            type: Boolean,
            required: true
        }
    },
    methods: {
        yesAction: function() {
            this.$emit('yes')
        },
        noAction: function() {
            this.$emit('no')
        }
    },
    watch: {
        visible: function(value) {
            if (value == true) {
                $(this.$refs.modal).modal('show')
            } else {
                $(this.$refs.modal).modal('hide')
            }
        }
    }
}
</script>
