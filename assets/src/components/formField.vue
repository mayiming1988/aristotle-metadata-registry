<template>
    <div :class="fieldClass">
        <component :is="tag" :required="required" :value="value" @input="emitInput"></component>
    </div>
</template>

<script>
export default {
    props: {
        fieldClass: {
            type: String,
            default: 'form-field'
        },
        tag: {
            type: String,
            default: 'input'
        },
        required: {
            type: Boolean,
            default: false
        },
        value: {
            type: String,
            default: ''
        },
        error: {
            type: Array,
        }
    },
    methods: {
        emitInput: function(event) {
            console.log(event)
            this.$emit('input', event.target.value)
        }
    }
}
</script>
