<template>
    <div class="inline-edit">
        <template v-if="editing">
            <api-errors class="small" :errors="errors"></api-errors>
            <input v-model="value"/>
            <button class="btn btn-default" @click="toggleEdit">Cancel</button>
            <button class="btn btn-primary" @click="saveValue">Save</button>
        </template>
        <template v-else>
            {{ value }}
            <button class="btn btn-default btn-sm" @click="toggleEdit">
                Edit <i class="fa fa-pencil" aria-hidden="true"></i>
            </button>
        </template>
    </div>
</template>

<script>
import apiRequest from 'src/mixins/apiRequest.js'
import apiErrors from '@/apiErrorDisplay.vue'

export default {
    mixins: [apiRequest],
    props: ['initial', 'submitUrl', 'fieldName'],
    components: {
        apiErrors
    },
    data: () => ({
        value: '',
        editing: false
    }),
    created: function() {
        this.value = this.initial
    },
    methods: {
        toggleEdit: function() {
            this.editing = !this.editing
        },
        saveValue: function() {
            let data = {}
            data[this.fieldName] = this.value
            this.patch(this.submitUrl, data)
            .then(() => {
                this.editing = false
            })
        }
    }
}
</script>

<style>
.inline-edit {
    display: inline-block;
}
</style>
