<template>
    <component :is="tag" :name="name" :class="fieldClass" :value="value" @input="emitOnInput" @change="emitOnChange">
        <option v-for="option in options" :key="option[0]" :value="option[0]" :selected="option[0] == value">{{ option[1] }}</option>
    </component>
</template>

<script>
export default {
    props: {
        tag: {
            type: [String, Object],
            default: 'input'
        },
        name: {
            type: String,
            required: true
        },
        value: {
            type: [String, Number],
        },
        fieldClass: {
            type: String,
            default: 'form-control'
        },
        options: {
            type: Array,
            default: function() {
                return []
            }
        },
        helpText: {
            type: String,
            required : false,
        }
    },
    methods: {
        emitOnInput: function(event) {
            if (this.tag != 'select')  {
                if (typeof event == "string") {
                    this.$emit('input', event)
                } else {
                    this.$emit('input', event.target.value)
                }
            }
        },
        emitOnChange: function(event) {
            // Need to use change since ie11 doesnt fire input events
            // for select elements :(

            if (this.tag == 'select') {
                this.$emit('input', event.target.value)
            }
        },
        hasOptions: function() {
            return Object.keys(this.options) > 0
        }
    }
}
</script>
