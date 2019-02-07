<template>
    <baseForm
        :fields="fields"
        :fe_errors="fe_errors"
        :errors="errors"
        v-model="formData">
        <template slot="after">
            <button class="btn btn-primary" @click="submit">Submit</button>
        </template>
    </baseForm>
</template>

<script>
import yaml from 'js-yaml'
import Ajv from 'ajv'

import baseForm from '@/forms/baseForm.vue'
import yamlEditor from '@/yamlEditor.vue'

export default {
    components: {
        baseForm
    },
    props: {
        schema: {
            type: String
        },
        initial: {
            type: Object,
            default: () => ({
                rules: ''
            })
        },
        errors: {
            type: Object
        }
    },
    created: function() {
        this.schemaObj = JSON.parse(this.schema)
        this.formData = this.initial
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
    }),
    methods: {
        submit: function() {
            let data = yaml.safeLoad(this.formData.rules)
            let ajv = new Ajv()
            let valid = ajv.validate(this.schemaObj, data)
            if (!valid) {
                let errors = ajv.errorsText(ajv.errors, {separator: ','}).split(',')
                this.fe_errors['rules'] = errors
            } else {
                this.fe_errors['rules'] = []
                this.$emit('submit', this.formData)
            }
        }
    }
}
</script>
