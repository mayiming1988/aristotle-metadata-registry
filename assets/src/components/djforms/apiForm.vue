<template>
    <Form
        :fields="fields"
        :initial="initial"
        :errors="errors"
        @submit="submitData">
    </Form>
</template>

<script>
import apiRequest from 'src/mixins/apiRequest.js'
import Form from '@/djforms/form.vue'

export default {
    components: {
        Form
    },
    mixins: [apiRequest],
    props: {
        dataFields: {
            type: String
        },
        dataInitial: {
            type: String,
            default: '{}'
        },
        url: {
            type: String
        }
    },
    created: function() {
        this.fields = JSON.parse(this.dataFields)
        this.initial = JSON.parse(this.dataInitial)
    },
    methods: {
        submitData: function(data) {
            this.post(url, data)
        }
    }
}
</script>
