<template>
    <baseForm 
        v-model="formData"
        :fields="fields" 
        :errors="errors" 
        :showLabels="showLabels" 
        :fe_errors="$v.formData">
        <template slot="after">
            <button class="btn btn-primary" @click="emitData">Submit</button>
        </template>
    </baseForm>
</template>

<script>
import { validationMixin } from 'vuelidate'
import getValidations from 'src/lib/forms/getValidations.js'

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
    validations() {
        return {
            formData: getValidations(this.fields)
        }
    },
    created: function() {
        if (this.initial) {
            this.formData = this.initial
        }
    },
    methods: {
        emitData: function() {
            if (!this.$v.invalid) {
                this.$emit('submit', this.formData)
            }
        }
    }
}
</script>
