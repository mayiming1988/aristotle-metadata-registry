<template>
    <div class="vue-form" :class="{'form-inline': inline}">
        <slot name="before"></slot>
        <bsFieldWrapper v-for="(fielddata, name) in fields" :name="name" :label="fielddata.label" :displayLabel="showLabels" :hasErrors="hasErrors(name)">
            <singleError :feError="getFrontendError(name)" :beErrors="getBackendErrors(name)"></singleError>
            <formField 
            :tag="fielddata.tag" 
            :name="name" 
            :placeholder="placeholder(name)"
            :options="fielddata.options"
            :value="value[name]" 
            @input="fieldInput(name, $event)"
            v-validate="fielddata.rules"
            :data-vv-scope="scope">
            </formField>
        </bsFieldWrapper>
        <button v-if="showSubmit" class="btn btn-primary" type="submit" @click="submitClicked">Submit</button>
        <slot name="after"></slot>
    </div>
</template>

<script>
import { capitalize } from 'src/lib/utils.js'

import singleError from '@/forms/singleError.vue'
import formField from '@/forms/formField.vue'
import bsFieldWrapper from '@/forms/bsFieldWrapper.vue'

export default {
    components: {
        bsFieldWrapper,
        formField,
        singleError
    },
    props: {
        scope: {
            type: String,
            default: 'form'
        },
        fields: {
            type: Object
        },
        value: {
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
        },
        showLabels: {
            type: Boolean,
            default: true
        }
    },
    methods: {
        mounted: function() {
            this.$validator.validate()
        },
        hasErrors: function(field_name) {
            let hasfe = this.fe_errors.has(field_name, this.scope)
            let hasbe = (this.errors && this.errors[field_name])
            return hasfe || hasbe
        },
        getFrontendError: function(field_name) {
            return this.fe_errors.first(field_name, this.scope)
        },
        getBackendErrors: function(field_name) {
            if (this.errors) {
                if (this.errors[field_name] != undefined) {
                    return this.errors[field_name]
                }
            }
            return []
        },
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
            this.$validator.validate().then((result) => {
                if (result) {
                    this.$emit('submitted', this.value)
                }
            })
        },
        fieldInput: function(fname, value) {
            // Emit a shallow copy, since we shouldn't alter props directly
            let copy = Object.assign({}, this.value)
            copy[fname] = value
            this.$emit('input', copy)
        }
    }
}
</script>

<style>
.form-inline .form-group {
    margin-right: 6px;
}
.form-inline .formset-fe-error {
    display: block;
}
.form-inline label {
    display: block;
}
</style>
