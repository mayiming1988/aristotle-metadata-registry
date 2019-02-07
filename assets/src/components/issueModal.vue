<template>
  <modal :value="value" title="Create Issue" @input="emitClose">
    <api-errors :errors="errors"></api-errors>
    <form-field name="name">
      <input id="name" class="form-control" v-model="formdata.name" />
    </form-field>
    <form-field name="description">
      <textarea id="description" class="form-control ta-fixed-width" v-model="formdata.description"></textarea>
    </form-field>
    <div slot="footer">
      <button type="button" class="btn btn-default" @click="emitClose">Close</button>
      <button type="button" class="btn btn-primary" @click="createIssue">Create Issue</button>
    </div>
  </modal>
</template>

<script>
import { Modal } from 'uiv'
import formField from '@/forms/bsFieldWrapper.vue'
import apiErrors from '@/apiErrorDisplay.vue'
import apiRequest from 'src/mixins/apiRequest.js'

export default {
    mixins: [apiRequest],
    components: {
        Modal,
        formField,
        apiErrors
    },
    props: ['iid', 'value', 'url'],
    data: () => ({
        formdata: {
            name: '',
            description: ''
        }
    }),
    methods: {
        emitClose: function() {
            this.$emit('input', false)
        },
        createIssue: function() {
            let postdata = this.formdata
            postdata['item'] = this.iid
            let promise = this.post(this.url, postdata)
            promise.then((response) => {
                // If issue created and url returned
                if (response.status == 201 && response.data['url']) {
                    this.redirect(response.data['url'])
                }
            })
        }
    }
}
</script>
