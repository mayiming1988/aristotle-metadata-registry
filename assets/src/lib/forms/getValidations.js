import { required, minLength, maxLength } from 'vuelidate/lib/validators'

export default function(djfields) {
    let validations = {}
    for (let fname in djfields) {
        let field = djfields[fname]
        let rules = field.rules

        let vuerules = {}
        if (rules.required) {
            vuerules['required'] = required
        }
        if (rules.min_length) {
            vuerules['minLength'] = minLength(rules.min_length)
        }
        if (rules.max_length) {
            vuerules['maxLength'] = maxLength(rules.max_length)
        }
        validations[fname] = vuerules
    }
    return validations
}
