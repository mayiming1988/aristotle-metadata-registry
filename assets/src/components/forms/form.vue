<template>
    <div class="vue-form" :class="{'form-inline': inline}">
        <apiErrors :errors="errors"></apiErrors>
        <bsFieldWrapper v-for="(fielddata, name) in fields" :name="getName(name)" :label="fielddata.label" :displayLabel="!inline" :hasErrors="fe_errors.has(getName(name))">
            <span class="text-danger" v-if="!inline">{{ fe_errors.first(getName(name)) }}</span>
            <formField 
            :tag="fielddata.tag" 
            :name="getName(name)" 
            :placeholder="placeholder(name)"
            :options="fielddata.options"
            :value="formData[name]" 
            @input="fieldInput(name, $event)"
            v-validate="fielddata.rules">
            </formField>
        </bsFieldWrapper>
        <button v-if="showSubmit" class="btn btn-primary" type="submit" @click="submitClicked">Submit</button>
    </div>
</template>

<script>
import { capitalize } from 'src/lib/utils.js'

import apiErrors from '@/apiErrorDisplay.vue'
import formField from '@/forms/formField.vue'
import bsFieldWrapper from '@/forms/bsFieldWrapper.vue'

export default {
    components: {
        apiErrors,
        bsFieldWrapper,
        formField
    },
    props: {
        fieldPrefix: {
            type: String,
            default: ''
        },
        fields: {
            type: Object
        },
        initial: {
            type: Object
        },
        errors: {
            type: Object
        },
        inline: {
            type: Boolean,
            default: false
        },
        showSubmit: {
            type: Boolean,
            default: true
        }
    },
    data: () => ({
        formData: {}
    }),
    created: function() {
        if (this.initial) {
            this.formData = this.initial
        }
        for (let key of Object.keys(this.fields)) {
            if (this.formData[key] === undefined) {
                this.formData[key] = ''
            }
        }
    },
    methods: {
        placeholder: function(field) {
            if (this.inline) {
                if (this.fields[field]['label']) {
                    return this.fields[field]['label']
                } else {
                    return capitalize(field)
                }
            } else {
                return ''
            }
        },
        submitClicked: function() {
            this.$emit('submitted', this.formData)
        },
        getName: function(name) {
            if (this.fieldPrefix) {
                return this.fieldPrefix + name
            } else {
                return name
            }
        },
        fieldInput: function(fname, value) {
            console.log(value)
            this.formData[fname] = value
            this.$emit('input', this.formData)
        }
    }
}
</script>
