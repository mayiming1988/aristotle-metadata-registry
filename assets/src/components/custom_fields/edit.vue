<template>
    <FormSet 
        :fields="fields" 
        :initial="initial" 
        :url="url" 
        :dontSubmitFields="dontSubmit">
    </FormSet>
</template>

<script>
import FormSet from '@/forms/formSet.vue'

export default {
    components: {
        FormSet
    },
    props: ['dataFields', 'dataInitial', 'url'],
    data: () => ({
        dontSubmit: ['hr_type']    
    }),
    created: function() {
        this.fields = JSON.parse(this.dataFields)
        this.initial = JSON.parse(this.dataInitial)
    }
}
</script>
