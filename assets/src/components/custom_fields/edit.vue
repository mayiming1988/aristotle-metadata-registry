<template>
    <FormSet :fields="fields" :initial="initial"></FormSet>
</template>

<script>
import FormSet from '@/forms/formSet.vue'

export default {
    components: {
        FormSet
    },
    props: ['dataFields'],
    created: function() {
        this.fields = JSON.parse(this.dataFields)
    },
    data: () => ({
        initial: [
            {'name': 'wow'},
            {'name': 'pow'}
        ]
    })
}
</script>
