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

import validationMixin from 'src/mixins/validation.js'
import baseForm from '@/forms/baseForm.vue'
import yamlEditor from '@/yamlEditor.vue'

export default {
    mixins: [validationMixin],
    components: {
        baseForm
    },
    props: {
        schema: {
            type: String
        },
    },
    created: function() {
        this.schemaObj = JSON.parse(this.schema)
    },
    data: () => ({
        fields: {
            'ra': {
                'tag': 'input',
                'label': 'Registration Authority',
            },
            'rules': {
                'tag': yamlEditor,
                'label': 'Rules',
                'class': '',
            },
        },
        formData: {
            'ra': '',
            'rules': '- dsa',
        },
        fe_errors: {
            'ra': {$invalid: false},
            'rules': {$invalid: false}
        },
        errors: {}
    }),
    methods: {
        submit: function() {
            let data = yaml.safeLoad(this.formData.rules)
            console.log(data)
            let ajv = new Ajv()
            let valid = ajv.validate(this.schemaObj, data)
            if (!valid) {
                console.log(ajv.errorsText())
            } else {
                console.log('Valid!')
            }
        }
    }
}
</script>
