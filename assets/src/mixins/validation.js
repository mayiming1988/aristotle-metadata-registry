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
        multipleForms: false,
        fields: {}
    }),
    methods: {
        isFieldValid: function(field) {
            return !$v[this.formDataPropName][field].$invalid
        }
    },
    computed: {
        dataValid: function() {
            return !$v[this.formDataPropName].$invalid
        },
        validationErrors: function() {
            return $v[this.formDataPropName]
        }
    },
    validations: function() {
        let validations = {}
        let dataValidations = getValidations(this.fields)
        if (!this.multipleForms) {
            validations[this.formDataPropName] = dataValidations
            return validations
        } else {
            validations[this.formDataPropName] = {$each: dataValidations}
            return validations
        }
    }
}
