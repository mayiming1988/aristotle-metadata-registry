/* globals $v */
import { validationMixin } from 'vuelidate'
import getValidations from 'src/lib/forms/getValidations.js'

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
        getValidationErrors: function(dataPropName) {
            return this.$v[dataPropName]
        },
        getIndexValidationErrors: function(dataPropName, index) {
            return this.$v[dataPropName].$each[index]
        }
    },
}
