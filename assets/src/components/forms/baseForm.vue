<template>
    <div class="vue-form" :class="{'row': inline }" @>
        <slot name="before" />
        <!-- Each div is a field -->
        <div :key="name" v-for="(fielddata, name) in fields">
            <div v-if="displayField(name, showChoiceField)">
            <bsFieldWrapper :help-text="fielddata.help_text" :key="name" :name="name" :label="fielddata.label" :display-label="showLabels" :has-errors="hasErrors(name)" :column="inline">
                    <singleError :fe-errors="getFrontendError(name)" :be-errors="getBackendErrors(name)" :column="inline" />
                    <formField
                            :tag="fielddata.tag"
                            :name="name"
                            :field-class="getFieldClass(fielddata.class)"
                            :placeholder="placeholder(name)"
                            :options="fielddata.options"
                            :value="value[name]"
                            @input="fieldInput(name, $event)"
                    />
                </bsFieldWrapper>
        </div>
        </div>
            <slot name="after" />
    </div>
</template>

<script>
    import {capitalize} from 'src/lib/utils.js'

    import singleError from '@/forms/singleError.vue'
    import formField from '@/forms/formField.vue'
    import bsFieldWrapper from '@/forms/bsFieldWrapper.vue'

    /*
    Base form with v-model support
    */
    export default {
        components: {
            bsFieldWrapper,
            formField,
            singleError
        },
        props: {
            fields: {
                type: Object,
                required: true
            },
            value: {
                type: Object
            },
            errors: {
                type: Object
            },
            fe_errors: {
                type: Object,
                required: true
            },
            inline: {
                type: Boolean,
                default: false
            },
            showLabels: {
                type: Boolean,
                default: true
            },
            showChoiceField: {
                type: Boolean,
                default: false,
            }
        },
        methods: {
            displayField: function(name, displayField) {
                if (name !== 'choices') {
                    return true
                }
                else if (name == 'choices' && displayField == true) {
                    return true
                }
                else {
                    return false
                }
            },

            hasErrors: function (field_name) {
                let hasfe = (this.fe_errors != undefined && this.fe_errors[field_name] != undefined)
                let hasbe = (this.errors != undefined && this.errors[field_name] != undefined)
                return hasbe || hasfe
            },
            getFrontendError: function (field_name) {
                if (this.fe_errors) {
                    return this.fe_errors[field_name]
                } else {
                    return []
                }
            },
            getBackendErrors: function (field_name) {
                if (this.errors) {
                    return this.errors[field_name]
                } else {
                    return []
                }
            },
            getFieldClass: function (fielddata_class) {
                if (fielddata_class === undefined) {
                    return 'form-control'
                } else {
                    return fielddata_class
                }
            },
            placeholder: function (field_name) {
                if (this.inline) {
                    if (this.fields[field_name]['label'] != undefined) {
                        return this.fields[field_name]['label']
                    } else {
                        return capitalize(field_name)
                    }
                } else {
                    return ''
                }
            },
            fieldInput: function (fname, value) {
                // Emit a shallow copy, since we shouldn't alter props directly
                let copy = Object.assign({}, this.value)
                copy[fname] = value
                this.$emit('input', copy)
            }
        },

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
