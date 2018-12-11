export default function(errors) {
    // Get an error message from a vuelidate object
    if (errors.$invalid) {
        if (!errors.required) {
            return 'This field is required'
        }
        if (!errors.maxLength) {
            return 'This field must contain less than ' + 
                errors.$params.maxLength.max.toString() + ' characters'
        }
        if (!errors.minLength) {
            return 'This field must contain at least ' + 
                errors.$params.maxLength.max.toString() + ' characters'
        }
    }
    return ''
}
