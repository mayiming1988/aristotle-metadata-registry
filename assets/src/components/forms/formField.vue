<template>
    <component :is="tag" :id="name" :class="fieldClass" :value="value" @input="emitInput"></component>
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
            type: String,
            default: ''
        },
        fieldClass: {
            type: String,
            default: 'form-control'
        }
    },
    methods: {
        emitInput: function(event) {
            this.$emit('input', event.target.value)
        }
    }
}
</script>
