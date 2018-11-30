<template>
    <Form :fields="fields" :initial="initial"></Form>
</template>

<script>
import Form from '@/form.vue'

export default {
    components: {
        Form
    },
    data: () => ({
        fields: {
            'name': {
                'tag': 'input',
                required: false
            }
        },
        initial: {
            'name': 'wow'
        }
    })
}
</script>
