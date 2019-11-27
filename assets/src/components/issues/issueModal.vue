<template>
    <modal :value="value" :title="actionText" size="lg" @input="emitClose">
        <api-errors :errors="errors"></api-errors>
        <form-field name="name">
            <input id="name" class="form-control" v-model="formdata.name" />
        </form-field>
        <form-field name="description">
            <textarea id="description" class="form-control ta-fixed-width" v-model="formdata.description"></textarea>
        </form-field>
        <template v-if="haslabelOptions">
            <form-field name="labels">
                <select-tagger v-model="formdata.labels" :options="labelOptions" />
            </form-field>
        </template>
        <template v-if="!haslabelOptions">
            <label>Labels</label>
            <p><em>
            <template v-if="hasStewardOrganisationName">
                The Stewardship Organisation this item belongs to has not set up any
                    issues labels.
            </template>
            <template v-else>
                This item doesn't belong to a Stewardship Organisation, so no labels can be applied.
            </template>
            </em></p>
        </template>
        <template v-if="isFields">
            <h3 class="divider">Proposed changes</h3>
            <template v-if="!edit">
                <select v-model="formdata.proposal_field">
                    <option value="">None</option>
                    <option v-for="f in fields" :value="f.name" :key="f.name">{{ capitalize(f.name) }}</option>
                </select>
                <small>Only the selected field will be proposed as a change</small>
            </template>
            <template v-if="formdata.proposal_field">
                <h4>Value for {{ capitalize(formdata.proposal_field) }}</h4>
                <form-field :name="formdata.proposal_field" :displayLabel="false">
                    <template v-if="isHtml(formdata.proposal_field)">
                        <html-editor v-model="proposals[formdata.proposal_field]" :json-config="htmlEditorConfig" />
                    </template>
                    <template v-else>
                        <textarea v-model="proposals[formdata.proposal_field]" class="form-control ta-fixed-width" />
                    </template>
                </form-field>
            </template>
        </template>
        <div slot="footer">
            <button type="button" class="btn btn-default" @click="emitClose">Close</button>
            <saving v-if="loading" />
            <button v-if="!loading" type="button" class="btn btn-primary" @click="saveIssue">
                {{ actionText }}
            </button>
        </div>
    </modal>
</template>

<script>
import htmlEditor from '@/htmlEditor.vue'
import Modal from 'uiv/src/components/modal/Modal.vue'
import formField from '@/forms/bsFieldWrapper.vue'
import apiErrors from '@/apiErrorDisplay.vue'
import apiRequest from 'src/mixins/apiRequest.js'
import saving from '@/saving.vue'
import selectTagger from '@/tags/selectTagger.vue'
import { capitalize } from 'src/lib/utils.js'

export default {
    mixins: [apiRequest],
    components: {
        'modal': Modal,
        'form-field': formField,
        'api-errors': apiErrors,
        'saving': saving,
        'html-editor': htmlEditor,
        'select-tagger': selectTagger
    },
    props: {
        iid: {
            type: String,
            required: true
        },
        url: {
            type: String,
            required: true
        },
        value: {
            type: Boolean,
            default: false
        },
        initial: {
            type: String,
            default: ''
        },
        // Current state of item's fields
        itemFieldsJson: {
            type: String,
            default: '{}'
        },
        // Fields we can propose changes for
        proposeFields: {
            type: String,
            default: '[]'
        },
        // Whether we are editing an issue instead of creating
        edit: {
            type: Boolean,
            default: false
        },
        htmlEditorConfig: {
            type: String,
            default: '{}'
        },
        // Json map of label ids to label names
        allLabelsJson: {
            type: String,
            required: true
        },
        // Name of the Stewardship Organisation this item belongs to - if any
        stewardOrganisationName: {
            type: String,
            default: ''
        }
    },
    data: () => ({
        html: 'Spicy',
        // Proposed changes for different fields
        proposals: {},
        // Fields we can propose changes for
        fields: [],
        // All labels that could be added to this issue
        // Array of options objects to be passed to selectTagger
        labelOptions: [],
        // Data to be posted
        formdata: {
            name: '',
            description: '',
            proposal_field: '',
            proposal_value: '',
            labels: []
        },
        // Map of fields to whether html
        htmlMap: new Map()
    }),
    created: function() {
        if (!this.edit) {
            // When creating new proposals set initial values from item
            this.proposals = JSON.parse(this.itemFieldsJson)
        } else {
            // Set formdata from initial
            this.formdata = JSON.parse(this.initial)
            // Set proposal value
            this.proposals[this.formdata.proposal_field] = this.formdata.proposal_value
            // Make sure formdata labels are strings
            for (let i in this.formdata.labels) {
                if (typeof this.formdata.labels[i] === "number") {
                    this.formdata.labels[i] = this.formdata.labels[i].toString()
                }
            }
        }
        this.fields = JSON.parse(this.proposeFields)
        // Build label options
        let labels = JSON.parse(this.allLabelsJson)
        for (let [id, name] of Object.entries(labels)) {
            this.labelOptions.push({value: id, text: name})
        }
        // Create map of fields to whether html
        for (let f of this.fields) {
            this.htmlMap.set(f.name, f.html)
        }
    },
    methods: {
        capitalize: capitalize,
        emitClose: function() {
            this.$emit('input', false)
        },
        saveIssue: function() {
            if (!this.loading) {
                // Get data
                let postdata = this.formdata
                postdata['item'] = this.iid
                // Set final value for proposed change
                if (postdata.proposal_field) {
                    postdata['proposal_value'] = this.proposals[postdata.proposal_field]
                }
                // determine http method
                let method = 'post'
                if (this.edit) {
                    method = 'put'
                }
                let promise = this.request(this.url, postdata, {}, method)
                promise.then((response) => {
                    // If 200 status and url returned
                    if (response.status >= 200 && response.status < 300 && response.data['url']) {
                        this.redirect(response.data['url'])
                    }
                })
            }
        },
        /* Return whether a field should be rendered as html or not */
        isHtml: function(field) {
            return (this.htmlMap.get(field) === true)
        },
    },
    computed: {
        isFields: function() {
            return Array.isArray(this.fields)
        },
        haslabelOptions: function() {
            return (Array.isArray(this.labelOptions) && this.labelOptions.length > 0)
        },
        hasStewardOrganisationName: function() {
            return this.stewardOrganisationName != ""
        },
        actionText: function() {
            let action = 'Create'
            if (this.edit) {
                action = 'Edit'
            }
            return action + ' Issue'
        }
    }
}
</script>

<style>
.divider {
    width: 100%;
    display: inline-block;
}
</style>
