<template>
    <Form :fields="fields" :initial="initial" :inline="true"></Form>
</template>

<script>
import Form from '@/forms/form.vue'

export default {
    components: {
        Form
    },
    props: ['dataFields'],
    created: function() {
        this.fields = JSON.parse(this.dataFields)
    },
    data: () => ({
        initial: {
            'name': 'wow'
        }
    })
}
</script>
