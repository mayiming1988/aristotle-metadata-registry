<template>
    <component :is="tag" :name="name" :class="fieldClass" :value="value" @input="emitInput">
        <option v-for="option in options" :value="option[0]" :selected="option[0] == value">{{ option[1] }}</option>
    </component>
</template>

<script>
export default {
    props: {
        tag: {
            type: String,
            default: 'input'
        },
        name: {
            type: String,
            required: true
        },
        value: {
            type: [String, Number],
            default: ''
        },
        fieldClass: {
            type: String,
            default: 'form-control'
        },
        options: {
            type: Array,
            default: []
        }
    },
    methods: {
        emitInput: function(event) {
            this.$emit('input', event.target.value)
        },
        hasOptions: function() {
            return Object.keys(this.options) > 0
        }
    }
}
</script>
