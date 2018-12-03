<template>
    <div class="vue-formset">
        <draggable :list="formsData" :options="sortableConfig">
            <Form 
                v-for="(item, index) in formsData" 
                v-model="formsData[index]"
                :key="index" 
                :fields="fields" 
                :inline="true"
                :scope="getScope(index)"
                :showSubmit="false">
                <template slot="before">
                    <i class="fa fa-bars pull-left grabber"></i>
                </template>
                <template slot="after">
                    <button class="btn btn-danger" @click="deleteRow(index)">Delete</button>
                </template>
            </Form>
        </draggable>
        <button class="btn btn-success" @click="addRow">Add</button>
        <button class="btn btn-primary" @click="submitFormSet">Submit</button>
    </div>
</template>

<script>
import Form from '@/forms/form.vue'
import draggable from 'vuedraggable'

export default {
    components: {
        draggable,
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
        sortableConfig: {
            handle: '.grabber'
        },
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
