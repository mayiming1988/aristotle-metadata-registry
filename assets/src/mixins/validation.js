import { validationMixin } from 'vuelidate'
import getValidations from 'src/lib/forms/getValidations.js'
import getErrorMsg from 'src/lib/forms/getErrorMsg.js'

/*
 * Wrap validation in our own mixin
 * so that it's easier to change validation libraries
 * or add extra functionality
 */
export default {
    mixins: [validationMixin],
    data: () => ({
        formDataPropName: 'formData',
        multipleForms: false
    }),
    methods: {
        isFieldValid: function(field) {
            return !this.$v[this.formDataPropName][field].$invalid
        },
        getValidations: function(fields, dataPropName, multipleForms=false) {
            let validations = {}
            let dataValidations = getValidations(fields)
            if (!multipleForms) {
                validations[dataPropName] = dataValidations
                return validations
            } else {
                validations[dataPropName] = {$each: dataValidations}
                return validations
            }
        },
        isDataValid: function(dataPropName) {
            return !this.$v[dataPropName].$invalid
        },
        getErrorMessages: function(errors) {
            let error_messages = {}
            for (let key in errors) {
                if (key.charAt(0) != '$') {
                    let error = errors[key]
                    if (error.$invalid) {
                        let msg = getErrorMsg(error)
                        error_messages[key] = [msg]
                    }
                }
            }
            return error_messages
        },
        getValidationErrors: function(dataPropName) {
            let errors = this.$v[dataPropName]
            return this.getErrorMessages(errors)
        },
        getIndexValidationErrors: function(dataPropName, index) {
            let errors = this.$v[dataPropName].$each[index]
            return this.getErrorMessages(errors)
        }
    },
}
