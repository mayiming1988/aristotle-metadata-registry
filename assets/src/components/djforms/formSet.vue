<template>
    <div class="vue-formset">
        <draggable :list="formsData" :options="sortableConfig">
            <div class="row container" v-for="(item, index) in formsData" v-bind:key="index">
                <div class="col-md-10">
                    <div class="panel panel-info">
                        <div class="panel-heading" role="button" @click="toggleAccordion(index)">
                            <h4 class="panel-title">
                                <i class="fa fa-lg fa-bars grabber" />
                                {{ item.name }}: {{ getAllowedModelName(item.allowed_model) }}
                            </h4>
                        </div>
                        <collapse v-model="showAccordion[index]">
                            <div class="panel-body">
                                <baseForm
                                        @input="addChoiceField"
                                        v-model="formsData[index]"
                                        :key="item.vid"
                                        :fields="fields"
                                        :inline="false"
                                        :errors="getError(item.vid)"
                                        :fe_errors="getIndexValidationErrors('formsData', index)"
                                        :showSubmit="false"
                                        :showLabels="true"
                                        :showChoiceField="displayChoiceField(item.vid)"
                                >
                                    <template v-if="showDeleteItem(item.new)" slot="after">
                                        <div class="col-md-1">
                                            <button class="btn btn-danger" @click="deleteRow(index)">
                                                Delete
                                            </button>
                                        </div>
                                    </template>
                                </baseForm>
                            </div>
                        </collapse>
                    </div>
                </div>
            </div>
        </draggable>
        <div class="vue-formset-button-group">
            <button class="btn btn-success" @click="addRow">
                {{ addButtonMessage }}
            </button>
            <button class="btn btn-primary" @click="submitFormSet">
                Submit Edits
            </button>
        </div>
    </div>
</template>

<script>
    import validationMixin from 'src/mixins/validation.js'
    import baseForm from '@/forms/baseForm.vue'
    import draggable from 'vuedraggable'
    import Collapse from 'uiv/src/components/collapse/Collapse.vue'
    /*
    Formset with validation,
    emits a submit event
    use apiFormset in django templates
    */
    export default {
        components: {
            Collapse,
            draggable,
            baseForm,
        },
        mixins: [validationMixin],
        props: {
            // List of the available fields
            fields: {
                type: Object,
            },
            allowed: {
                type: Object,
            },
            initial: {
                type: Array,
            },
            addButtonMessage: {
                type: String,
                default: 'Add',
            },
            showDelete: {
                type: Boolean,
                default: true
            },
            orderField: {
                type: String,
                default: 'order'
            },
            showLabels: {
                type: Boolean,
                default: true,
            },
            errors: {
                type: Array,
            },
        },
        data: () => ({
            message: '',
            sortableConfig: {
                handle: '.grabber',
            },
            stripFields: ['vid', 'new'],
            error_map: {},
            formsData: [],
            nextVid: 0,
            showAccordion: [],
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

                // Populate the showAccordion list
                this.showAccordion.push(false)
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
            },
            displayChoices: function () {
                // Display choices fields is a dictionary of true/false values to allow the baseForm component
                // to determine whether or not to display the choice form field
                let displayChoices = {};

                for (let i = 0; i < this.formsData.length; i++) {
                    displayChoices[i] = this.formsData[i]['type'] === 'enum';
                }
                return displayChoices
            }
        },
        methods: {
            getAllowedModelName: function (id) {
                if (id == null || id == '') {
                    return 'All'
                }
                else {
                    return this.allowed[id.toString()]
                }
            },
            displayChoiceField: function (vid) {
                return this.displayChoices[vid]
            },
            getError: function (vid) {
                return this.error_map[vid]
            },
            addRow: function () {
                this.formsData.push(this.default)
                this.nextVid += 1
                this.showAccordion = this.showAccordion.map(() => false)
                this.showAccordion.push(true)
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
            toggleAccordion: function (index) {
                if (this.showAccordion[index]) {
                    this.$set(this.showAccordion, index, false)
                } else {
                    this.showAccordion = this.showAccordion.map((v, i) => i === index)
                }
            },
            addChoiceField: function (form) {
                if (form.type == 'enum') {
                    this.displayChoices[form.vid] = true
                    this.formsData[form.vid]['display'] = false
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
        margin-bottom: 20px;
    }
</style>
