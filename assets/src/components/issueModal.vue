<template>
    <modal :value="value" :title="actionText" size="lg" @input="emitClose">
    <api-errors :errors="errors"></api-errors>
    <form-field name="name">
        <input id="name" class="form-control" v-model="formdata.name" />
    </form-field>
    <form-field name="description">
        <textarea id="description" class="form-control ta-fixed-width" v-model="formdata.description"></textarea>
    </form-field>
    <template v-if="isFields">
        <h3>Proposed changes</h3>
        <div class="panel-group">
            <div v-for="(f, index) in fields" class="panel panel-default" :key="index">
                <div class="panel-heading" role="button" @click="toggleAccordion(index)">
                    <h4 class="panel-title">{{ capitalize(f.name) }}</h4>
                </div>
                <collapse v-model="showAccordion[index]">
                <div class="panel-body">
                    <textarea class="form-control ta-fixed-width" v-model="proposals[f.name]" />
                </div>
                </collapse>
            </div>
        </div>
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
import Modal from 'uiv/src/components/modal/Modal.vue'
import Collapse from 'uiv/src/components/collapse/Collapse.vue'
import formField from '@/forms/bsFieldWrapper.vue'
import apiErrors from '@/apiErrorDisplay.vue'
import apiRequest from 'src/mixins/apiRequest.js'
import saving from '@/saving.vue'
import { capitalize } from 'src/lib/utils.js'

export default {
    mixins: [apiRequest],
    components: {
        Modal,
        Collapse,
        formField,
        apiErrors,
        saving,
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
            required: true
        },
        // Fields we can propose changes for
        proposeFields: {
            type: String,
            default: '{}'
        },
        // Whether we are editing an issue instead of creating
        edit: {
            type: Boolean,
            default: false
        }
    },
    data: () => ({
        showAccordion: [],
        proposals: {},
        formdata: {
            name: '',
            description: '',
            proposals: ''
        }
    }),
    created: function() {
        this.formdata = JSON.parse(this.initial)
        this.proposals = JSON.parse(this.formdata.proposals)
        this.fields = JSON.parse(this.proposeFields)
        // TODO Remove fields not in initial
        // Have accordian off by default
        for (let i = 0; i < this.fields.length; i++) {
            this.showAccordion.push(false)
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
                // TODO only save edited fields
                postdata['proposals'] = JSON.stringify(this.proposals)
                // determinal http method
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
        toggleAccordion: function(index) {
            if (this.showAccordion[index]) {
                this.$set(this.showAccordion, index, false)
            } else {
                this.showAccordion = this.showAccordion.map((v, i) => i === index)
            }
        }
    },
    computed: {
        isFields: function() {
            return Array.isArray(this.fields)
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
