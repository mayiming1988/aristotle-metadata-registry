<template>
    <div class="vue-formset">
        <draggable :list="formsData" :options="sortableConfig">
            <Form 
                v-for="(item, index) in formsData" 
                v-model="formsData[index]"
                :key="item.vid" 
                :fields="fields" 
                :inline="true"
                :scope="getScope(index)"
                :showSubmit="false">
                <template slot="before">
                    <i class="fa fa-lg fa-bars pull-left grabber"></i>
                </template>
                <template slot="after">
                    <button class="btn btn-danger" @click="deleteRow(index)">Delete</button>
                </template>
            </Form>
        </draggable>
        <div class="vue-formset-button-group">
            <button class="btn btn-success" @click="addRow">Add</button>
            <button class="btn btn-primary" @click="submitFormSet">Submit</button>
        </div>
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
        orderField: {
            type: String,
            default: 'order'
        },
        initial: {
            type: Array
        },
        dontSubmitFields: {
            type: Array
        }
    },
    data: () => ({
        sortableConfig: {
            handle: '.grabber',
        },
        stripFields: ['vid'],
        formsData: []
    }),
    created: function() {
        if (this.initial) {
            this.formsData = this.initial
        }
        if (this.dontSubmitFields) {
            for (let field of this.dontSubmitFields) {
                this.stripFields.push(field)
            }
        }
        for (let i=0; i < this.formsData.length; i++) {
            // Add a vue id to each item as unique key
            this.formsData[i]['vid'] = i
        }
    },
    methods: {
        getScope: function(index) {
            return 'form' + index.toString()
        },
        addRow: function() {
            let newrow = {'vid': this.formsData.length}
            this.formsData.push(newrow)
        },
        deleteRow: function(index) {
            this.formsData.splice(index, 1)
        },
        postProcess: function() {
            let fdata = []
            for (let i=0; i < this.formsData.length; i++) {
                // Get shallow clone of item
                let item = Object.assign({}, this.formsData[i])
                // Remove unneeded fields
                for (let field of this.stripFields) {
                    delete item[field]
                }
                // Reorder
                item['order'] = i + 1
                fdata.push(item)
            }
            return fdata
        },
        submitFormSet: function() {
            let dataToSubmit = this.postProcess()
            console.log(dataToSubmit)
        }
    }
}
</script>

<style>
.grabber {
    padding-top: 5px;
}
.vue-formset-button-group {
    margin-top: 10px;
}
</style>
