<template>
    <div class="outer-formset">
        <alert v-if="message.length > 0" type="success">{{ message }}</alert>
        <FormSet 
            :fields="fields" 
            :initial="initial" 
            :errors="errors"
            :showLabeld="showLabels"
            :showDelete="showDelete"
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
        message: '',
        errors: []
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
        },
        showLabels: {
            type: Boolean,
            default: true
        },
        showDelete: {
            type: Boolean,
            default: true
        },
    },
    created: function() {
        this.fields = JSON.parse(this.dataFields)
        this.initial = JSON.parse(this.dataInitial)
    },
    methods: {
        onSubmit: function(data) {
            this.post(this.url, data)
            .then(() => {
                this.message = 'Custom Fields Updated'
            })
        }
    }
}
</script>
