<template>
    <div class="outer-formset">
        <alert v-if="message.length > 0" type="success">{{ message }}</alert>
        <FormSet 
            :fields="fields" 
            :initial="initial" 
            :errors="errors"
            @submit="onSubmit">
        </FormSet>
    </div>
</template>

<script>
import apiRequest from 'src/mixins/apiRequest.js'
import { Alert } from 'uiv'
import FormSet from '@/forms/formSet.vue'

export default {
    mixins: [apiRequest],
    components: {
        FormSet,
        Alert
    },
    data: () => ({
        message: ''
    }),
    props: {
        dataFields: {
            type: String
        },
        dataInitial: {
            type: String,
            default: '[]'
        },
        url: {
            type: String
        }
    },
    created: function() {
        this.fields = JSON.parse(this.dataFields)
        this.initial = JSON.parse(this.dataInitial)
        this.errors = []
    },
    methods: {
        onSubmit: function(data) {
            this.post(this.url, data).then((response) => {
                this.message = 'Custom Fields Updated'
            })
        }
    }
}
</script>
