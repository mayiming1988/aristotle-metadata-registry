<template>
  <modal :value="value" title="Create Issue" @input="emitClose">
    <form-field name="name">
      <input id="name" class="form-control" v-model="formdata.name" />
    </form-field>
    <form-field name="description">
      <textarea id="description" class="form-control" v-model="formdata.description" />
    </form-field>
    <div slot="footer">
      <button type="button" class="btn btn-default" @click="emitClose">Close</button>
      <button type="button" class="btn btn-primary" @click="createIssue">Create Issue</button>
    </div>
  </modal>
</template>

<script>
import { Modal } from 'uiv'
import formField from '../components/bsFormField.vue'
import apiRequest from '../mixins/apiRequest.js'

export default {
    mixins: [apiRequest],
    components: {
        Modal,
        formField
    },
    props: ['iid', 'value'],
    data: () => ({
        formdata: {
            name: '',
            description: ''
        },
        url: '/api/v4/issues/'
    }),
    methods: {
        emitClose: function() {
            this.$emit('input', false)
        },
        createIssue: function() {
            let postdata = this.formdata
            postdata['item'] = this.iid
            this.post(this.url, postdata)
        }
    }
}
</script>
