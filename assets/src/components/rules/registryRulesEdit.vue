<template>
    <editForm
        :initial="initial"
        :schema="schema"
        :errors="errors"
        @submit="submitData">
    </editForm>
</template>

<script>
import apiRequest from 'src/mixins/apiRequest.js'
import editForm from '@/rules/editForm.vue'

export default {
    mixins: [apiRequest],
    components: {
        editForm
    },
    props: {
        value: String,
        schema: String,
        api_url: String,
    },
    computed: {
        initial: function() {
            return {
                rules: this.value
            }
        }
    },
    methods: {
        submitData: function(data) {
            this.put(this.api_url, data)
        }
    }
}
</script>
