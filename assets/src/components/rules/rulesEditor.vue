<template>
    <div class="registry-rules-edit">
        <alert v-if="request_error" type="danger">{{ request_error }}</alert>
        <alert v-if="updated" type="success">
            Registry rules have been updated
        </alert>
        <editForm
            :initial="initial"
            :schema="schema"
            :errors="errors"
            @submit="submitData"
            @edit="closeAlert">
        </editForm>
    </div>
</template>

<script>
import { Alert } from 'uiv'
import apiRequest from 'src/mixins/apiRequest.js'
import editForm from '@/rules/editForm.vue'

export default {
    mixins: [apiRequest],
    components: {
        'editForm': editForm,
        'alert': Alert
    },
    data: () => ({
        updated: false
    }),
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
            this.put(this.api_url, data).then(() => {
                this.updated = true
            })
        },
        closeAlert: function() {
            this.updated = false
        }
    }
}
</script>
