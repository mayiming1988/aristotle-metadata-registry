<template>
    <Form :fields="fields" :initial="initial"></Form>
</template>

<script>
import Form from '@/forms/form.vue'

export default {
    components: {
        Form
    },
    data: () => ({
        fields: {
            'name': {
                'tag': 'input',
                'rules': {
                    required: true,
                    max: 7
                }
            }
        },
        initial: {
            'name': 'wow'
        }
    })
}
</script>
