<template>
  <div class="form-group" :class="{'has-error': hasErrors, 'col-md-2': column}">
    <label :class="{'sr-only': !displayLabel}" :for="name">{{ labelToDisplay }}</label>
    <small><em>{{ helpText }}</em></small>
    <slot></slot>
  </div>
</template>

<script>
import { capitalize } from 'src/lib/utils.js'
export default {
    props: {
        name: {
            type: String
        },
        label: {
            type: String
        },
        helpText: {
          type: String
        },
        displayLabel: {
            type: Boolean,
            default: true
        },
        hasErrors: {
            type: Boolean,
            default: false
        },
        column: {
            type: Boolean,
            default: false
        }
    },
    methods: {
        capitalize: capitalize
    },
    computed: {
        labelToDisplay: function() {
            if (this.label != undefined) {
                return this.label
            } else {
                return capitalize(this.name)
            }
        }
    }
}
</script>
