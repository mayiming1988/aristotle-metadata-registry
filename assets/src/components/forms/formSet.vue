<template>
    <div class="vue-formset">
        <Form 
            v-for="(item, index) in formsData" 
            v-model="formsData[index]"
            :key="index" 
            :fields="fields" 
            :inline="true"
            :scope="getScope(index)"
            :showSubmit="false">
            <button class="btn btn-danger" @click="deleteRow(index)">Delete</button>
        </Form>
        <button class="btn btn-success" @click="addRow">Add</button>
        <button class="btn btn-primary" @click="submitFormSet">Submit</button>
    </div>
</template>

<script>
import Form from '@/forms/form.vue'
export default {
    components: {
        Form
    },
    props: {
        fields: {
            type: Object
        },
        initial: {
            type: Array
        }
    },
    data: () => ({
        formsData: []
    }),
    created: function() {
        if (this.initial) {
            this.formsData = this.initial
        }
    },
    methods: {
        getPrefix: function(index) {
            return index.toString() + '-'
        },
        getScope: function(index) {
            return 'form' + index.toString()
        },
        addRow: function() {
            this.formsData.push({})
        },
        deleteRow: function(index) {
            this.formsData.splice(index, 1)
        },
        submitFormSet: function() {
            return 0
        }
    }
}
</script>
