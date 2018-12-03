<template>
    <div class="vue-form">
        <bsFieldWrapper v-for="(fielddata, name) in fields" :name="name">
            <span>{{ fe_errors.first(name) }}</span>
            <formField 
            :tag="fielddata.tag" 
            :name="name" 
            v-model="formdata[name]" 
            v-validate="fielddata.rules">
            </formField>
        </bsFieldWrapper>
        <button class="btn btn-primary" type="submit">Submit</button>
    </div>
</template>

<script>
import formField from '@/forms/formField.vue'
import bsFieldWrapper from '@/forms/bsFieldWrapper.vue'

export default {
    components: {
        bsFieldWrapper,
        formField
    },
    props: ['fields', 'initial'],
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
    }
}
</script>
