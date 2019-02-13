<template>
    <baseForm
        :fields="fields"
        :fe_errors="fe_errors"
        :errors="errors"
        v-model="formData">
        <template slot="after">
            <button class="btn btn-primary" @click="submit">
                Submit
            </button>
        </template>
    </baseForm>
</template>

<script>
import { safeLoad } from 'js-yaml/lib/js-yaml/loader.js'
import Ajv from 'ajv'

import baseForm from '@/forms/baseForm.vue'
import yamlEditor from '@/yamlEditor.vue'

export default {
    components: {
        baseForm
    },
    props: {
        schema: {
            type: String,
            required: true
        },
        initial: {
            type: Object,
            default: () => ({
                rules: ''
            })
        },
        errors: {
            type: Object,
            required: true
        },
    },
    created: function() {
        this.schemaObj = JSON.parse(this.schema)
        this.formData = this.initial
        this.ajv = new Ajv()
    },
    data: () => ({
        fields: {
            'rules': {
                'tag': yamlEditor,
                'label': 'Rules',
                'class': '',
            },
        },
        formData: {},
        fe_errors: {
            'rules': []
        },
        submitted : false,
    }),
    methods: {
        submit: function() {
            let data = safeLoad(this.formData.rules)
            let valid = this.ajv.validate(this.schemaObj, data)
            if (!valid) {
                let errors = this.ajv.errorsText(this.ajv.errors, {separator: ','}).split(',')
                this.fe_errors['rules'] = errors
            } else {
                this.fe_errors['rules'] = []
                this.$emit('submit', this.formData)
                this.submitted = true
            }
        }
    },
    watch: {
        formData: function() {
            if (this.submitted) {
                this.$emit('edit') // Emit edit when a change happens after a submit
                this.submitted = false
            }
        }
    }
}
</script>
