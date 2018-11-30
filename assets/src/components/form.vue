<template>
    <div class="vue-form">
        <template v-for="(fielddata, name) in fields">
            <label>{{ name }}</label>
            <formField :tag="fielddata.tags" :required="fielddata.required" v-model="formdata[name]"></formField>
        </template>
    </div>
</template>

<script>
import formField from '@/formField.vue'

export default {
    components: {
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
