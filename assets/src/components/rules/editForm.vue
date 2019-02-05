<template>
    <baseForm
        :fields="fields"
        :fe_errors="fe_errors"
        :errors="errors"
        :value="values">
    </baseForm>
</template>

<script>
import baseForm from '@/forms/baseForm.vue'
import yamlEditor from '@/yamlEditor.vue'

export default {
    components: {
        baseForm
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
        values: {
            'ra': '',
            'rules': '{}',
        },
        fe_errors: {
            'ra': {$invalid: false},
            'rules': {$invalid: false}
        },
        errors: {}
    })
}
</script>
