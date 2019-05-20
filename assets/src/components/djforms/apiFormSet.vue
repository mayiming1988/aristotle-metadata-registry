<template>
    <div class="outer-formset">
        <alert v-if="message.length > 0" type="success">{{ message }}</alert>
        <alert v-if="request_error.length > 0" type="danger">{{ request_error }}</alert>
        <FormSet 
            :fields="fields" 
            :initial="initial"
            :allowed="allowed"
            :errors="errors"
            :showLabels="showLabels"
            :showDelete="showDelete"
            @submit="onSubmit">
        </FormSet>
    </div>
</template>

<script>
import apiRequest from 'src/mixins/apiRequest.js'
import Alert from 'uiv/src/components/alert/Alert.vue'
import FormSet from '@/djforms/formSet.vue'

export default {
    mixins: [apiRequest],
    components: {
        FormSet,
        Alert
    },
    data: () => ({
        combine_errors: false, // Override from mixin
        message: '',
        errors: [],
    }),
    props: {
        dataFields: {
            type: String
        },
        dataInitial: {
            type: String,
            default: '[]'
        },
        dataAllowed: {
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
        this.allowed = JSON.parse(this.dataAllowed)
        this.fields = JSON.parse(this.dataFields)
        this.initial = JSON.parse(this.dataInitial)
    },
    methods: {
        onSubmit: function(data) {
            this.post(this.url, data)
            .then(() => {
                this.message = 'Custom Fields Updated'
            })
            .catch(() => {
                if (typeof this.errors === 'object' && this.errors['request'] != undefined) {
                    // Make sure errors is always an array
                    this.reqerror = this.errors['request']
                    this.errors = []
                }
            })
        }
    }
}
</script>
