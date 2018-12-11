<template>
    <baseForm 
        v-model="formData"
        :fields="fields" 
        :errors="errors" 
        :showLabels="showLabels" 
        :fe_errors="getValidationErrors('formData')">
        <template slot="after">
            <button class="btn btn-primary" @click="emitData">Submit</button>
        </template>
    </baseForm>
</template>

<script>
import validationMixin from 'src/mixins/validation.js'

import baseForm from '@/forms/baseForm.vue'

/*
Wraps base form with frontend validation, emits data to submit
Use apiForm in django template
*/
export default {
    components: {
        baseForm
    },
    mixins: [validationMixin],
    data: () => ({
        formData: {}
    }),
    props: {
        fields: {
            type: Object
        },
        inline: {
            type: Boolean,
            default: false
        },
        showLabels: {
            type: Boolean,
            default: true
        },
        errors: {
            type: Object
        },
        initial: {
            type: Object
        }
    },
    created: function() {
        if (this.initial) {
            this.formData = this.initial
        }
    },
    validations: function() {
        return this.getValidations(this.fields, 'formData')
    },
    methods: {
        emitData: function() {
            if (this.isDataValid('formdata')) {
                this.$emit('submit', this.formData)
            }
        }
    }
}
</script>
