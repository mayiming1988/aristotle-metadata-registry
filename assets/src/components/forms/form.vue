<template>
    <div class="vue-form" :class="{'form-inline': inline}">
        <apiErrors :errors="errors"></apiErrors>
        <bsFieldWrapper v-for="(fielddata, name) in fields" :name="name" :label="fielddata.label" :displayLabel="!inline" :hasErrors="fe_errors.has(name)">
            <span class="text-danger" v-if="!inline">{{ fe_errors.first(name) }}</span>
            <formField 
            :tag="fielddata.tag" 
            :name="name" 
            :placeholder="placeholder(name)"
            :options="fielddata.options"
            v-model="formdata[name]" 
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
        formdata: {}
    }),
    created: function() {
        if (this.initial) {
            this.formdata = this.initial
        }
        for (let key of Object.keys(this.fields)) {
            if (this.formdata[key] === undefined) {
                this.formdata[key] = ''
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
            this.$emit('submitted', this.formdata)
        }
    }
}
</script>
