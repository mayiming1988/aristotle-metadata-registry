<template>
    <div class="vue-formset">
        <div v-if="showLabels" class="row">
            <div class="col-md-1 text-center"><label>Order</label></div>
            <div v-for="(fielddata, name) in fields" class="col-md-2">
                <label v-if="fielddata.label">{{ fielddata.label }}</label>
            </div>
            <div v-if="showDelete" class="col-md-2"><label>Delete</label></div>
        </div>
        <draggable :list="formsData" :options="sortableConfig">
            <Form 
                v-for="(item, index) in formsData" 
                v-model="formsData[index]"
                :key="item.vid" 
                :fields="fields" 
                :inline="true"
                :errors="be_errors[item.vid]"
                :scope="getScope(index)"
                :showSubmit="false"
                :showLabels="false">
                <template slot="before">
                    <div class="col-md-1 text-center">
                        <i class="fa fa-lg fa-bars grabber"></i>
                    </div>
                </template>
                <template v-if="showDelete" slot="after">
                    <div class="col-md-2">
                        <button class="btn btn-danger" @click="deleteRow(index)">Delete</button>
                    </div>
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
        Form,
    },
    props: {
        fields: {
            type: Object
        },
        orderField: {
            type: String,
            default: 'order'
        },
        showLabels: {
            type: Boolean,
            default: true
        },
        showDelete: {
            type: Boolean,
            default: true
        },
        initial: {
            type: Array
        },
        errors: {
            type: Array
        }
    },
    data: () => ({
        message: '',
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
        for (let i=0; i < this.formsData.length; i++) {
            // Add a vue id to each item as unique key
            this.formsData[i]['vid'] = i
        }
    },
    computed: {
        be_errors: function() {
            let error_map = {}
            for (let i=0; i < this.errors.length; i++) {
                let err = this.errors[i]
                let vid = this.formsData[i]['vid']
                error_map[vid] = err
            }
            return error_map
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
            this.$emit('submit', dataToSubmit)
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
