<template>
    <div class="vue-formset">
        <table class="table table-striped table-responsive">

            <!-- Show labels -->
            <thead v-if="showLabels">

            <tr><label>Order</label></tr>

            <tr v-for="(fielddata, name) in fields" :key="name">
                <label v-if="fielddata.label">{{ fielddata.label }}</label>
            </tr>
            <tr v-if="showDelete" class="col-md-2"><label>Delete</label></tr>
            </thead>
            <tbody>
            <!-- Show forms -->
            <draggable :list="formsData" :options="sortableConfig">
                <baseForm
                        v-for="(item, index) in formsData"
                        v-model="formsData[index]"
                        :key="item.vid"
                        :fields="fields"
                        :inline="true"
                        :errors="getError(item.vid)"
                        :fe_errors="getIndexValidationErrors('formsData', index)"
                        :showSubmit="false"
                        :showLabels="false">

                    <template slot="before">
                        <div class="col-md-1 text-center">
                            <i class="fa fa-lg fa-bars grabber"></i>
                        </div>
                    </template>

                    <!-- Show delete items -->
                    <template v-if="showDeleteItem(item.new)" slot="after">
                        <div class="col-md-1">
                            <button class="btn btn-danger" @click="deleteRow(index)">Delete</button>
                        </div>

                    </template>
                </baseForm>
            </draggable>


        </table>
        <!-- Add and submit buttons -->
        <div class="vue-formset-button-group">
            <button class="btn btn-success" @click="addRow">Add</button>
            <button class="btn btn-primary" @click="submitFormSet">Submit</button>
        </div>
    </div>

</template>

<script>

    import validationMixin from 'src/mixins/validation.js'
    import baseForm from '@/forms/baseForm.vue'
    import draggable from 'vuedraggable'

    /*
    Formset with validation,
    emits a submit event
    use apiFormset in django templates
    */
    export default {
        components: {
            draggable,
            baseForm,
        },
        mixins: [validationMixin],
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
            stripFields: ['vid', 'new'],
            error_map: {},
            formsData: [],
            nextVid: 0
        }),
        created: function () {
            if (this.initial) {
                this.formsData = this.initial
                this.nextVid = this.formsData.length
            }
            for (let i = 0; i < this.formsData.length; i++) {
                // Add a vue id to each item as unique key
                this.formsData[i]['vid'] = i
                this.formsData[i]['new'] = false
            }
        },
        validations: function () {
            return this.getValidations(this.fields, 'formsData', true)
        },
        watch: {
            errors: function () {
                let error_map = {}
                for (let i = 0; i < this.errors.length; i++) {
                    let err = this.errors[i]
                    let vid = this.formsData[i]['vid']
                    error_map[vid] = err
                }
                this.error_map = error_map
            }
        },
        computed: {
            default: function () {
                let defaults = {vid: this.nextVid, new: true}
                for (let fname in this.fields) {
                    let field = this.fields[fname]
                    if (field.default != null) {
                        defaults[fname] = field.default
                    }
                }
                return defaults
            }
        },
        methods: {
            getError: function (vid) {
                return this.error_map[vid]
            },
            addRow: function () {
                this.formsData.push(this.default)
                this.nextVid += 1
            },
            deleteRow: function (index) {
                this.formsData.splice(index, 1)
            },
            postProcess: function () {
                let fdata = []
                for (let i = 0; i < this.formsData.length; i++) {
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
            submitFormSet: function () {
                if (this.isDataValid('formsData')) {
                    let dataToSubmit = this.postProcess()
                    this.$emit('submit', dataToSubmit)
                }
            },
            showDeleteItem: function (isnew) {
                if (this.showDelete) {
                    return true
                } else {
                    return isnew
                }
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
