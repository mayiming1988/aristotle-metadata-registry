<template>
    <div class="outer-formset">
        <alert v-if="message.length > 0" type="success">
            {{ message }}
        </alert>
        <alert v-if="errors.length > 0" type="danger">
            {{ errors }}
        </alert>
        <FormSet
                :fields="fields"
                :allowed="allowed"
                :initial="initial"
                :relatedModel="relatedModel"
                :addButtonMessage="addButtonMessage"
                :errors="errors"
                :showLabels="showLabels"
                :showDelete="showDelete"
                @submit="onSubmit"
        />
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
                type: String,
            },
            dataAllowed: {
                type: String,
                default: '[]',
            },
            dataInitial: {
                type: String,
                default: '[]',
            },
            dataRelatedModel: {
                type: String,
                default: "All"
            },
            dataAddButtonMessage: {
                type: String,
                default: 'Add',
            },
            showDelete: {
                type: Boolean,
                default: true,
            },
            url: {
                type: String,
            },
            showLabels: {
                type: Boolean,
                default: true,
            },
        },
        created: function () {
            this.allowed = JSON.parse(this.dataAllowed)
            this.fields = JSON.parse(this.dataFields)
            this.initial = JSON.parse(this.dataInitial)
            this.addButtonMessage = this.dataAddButtonMessage
            this.relatedModel = this.dataRelatedModel
        },
        methods: {
            onSubmit: function (data) {
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
                        this.errors = this.extractErrors(this.errors)
                    })
            },

            extractErrors: function (errors) {
                let parsed_errors = [];
                for (let error of errors) {
                    if (error.non_field_errors != undefined) {
                        // It's an validation error
                        parsed_errors.push(error.non_field_errors[0])
                    }
                }
                return parsed_errors.join('. ')

            }
        }
    }
</script>
