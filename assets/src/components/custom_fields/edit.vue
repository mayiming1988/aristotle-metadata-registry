<template>
    <FormSet :fields="fields" :initial="initial"></FormSet>
</template>

<script>
import FormSet from '@/forms/formSet.vue'

export default {
    components: {
        FormSet
    },
    props: ['dataFields', 'dataInitial'],
    created: function() {
        this.fields = JSON.parse(this.dataFields)
        this.initial = JSON.parse(this.dataInitial)
    },
    data: () => ({
        oldinitial: [
            {'id': 1, 'name': 'wow'},
            {'id': 2, 'name': 'pow'}
        ]
    })
}
</script>
