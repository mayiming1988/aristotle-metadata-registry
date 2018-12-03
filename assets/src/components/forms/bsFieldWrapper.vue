<template>
  <div class="form-group">
    <label :class="labelClass" :for="name">{{ capitalize(name) }}</label>
    <slot class="form-control"></slot>
  </div>
</template>

<script>
import { capitalize } from 'src/lib/utils.js'
export default {
    props: {
        name: {
            type: String
        },
        displayLabel: {
            type: Boolean,
            default: true
        }
    },
    methods: {
        capitalize: capitalize
    },
    computed: {
        labelClass: function() {
            if (!this.displayLabel) {
                return 'sr-only'
            } else {
                return ''
            }
        }
    }
}
</script>
