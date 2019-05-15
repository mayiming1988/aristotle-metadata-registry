<template>
    <div class="panel panel-default">
      <div class="panel-heading">
        <strong>
          <a class="blackLink" role="button" aria-expanded="false" aria-controls="" @click="toggle">
              {{ title }} <i class="fa" :class="iconClass" />
          </a>
        </strong>
      </div>
      <div ref="collapsePanel" class="collapse panel-body">
          <slot />
      </div>
    </div>
</template>

<script>
export default {
    props: {
        title: {
            type: String,
            required: true
        },
        caret: {
            type: Boolean,
            default: false
        }
    },
    data: () => ({
        open: false
    }),
    methods: {
        toggle: function() {
            let panel = $(this.$refs.collapsePanel)
            if (this.open) {
                panel.collapse('hide')
            } else {
                panel.collapse('show')
            }
            this.open = !this.open
        }
    },
    computed: {
        iconClass: function() {
            if (this.open) {
                return 'fa-caret-up'
            }
            return 'fa-caret-down'
        }
    }
}
</script>

<style>
a.blackLink {
    color: #333333;
}
</style>
