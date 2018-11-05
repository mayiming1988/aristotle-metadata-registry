<template>
  <modal :value="value" title="Create Issue" @input="emitClose">
    <form-field name="name">
      <input id="name" class="form-control" v-model="name" />
    </form-field>
    <form-field name="description">
      <textarea id="description" class="form-control" v-model="description" />
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

export default {
    components: {
        Modal,
        formField
    },
    props: ['iid', 'value'],
    data: () => ({
        name: '',
        description: ''
    }),
    methods: {
        emitClose: function() {
            this.$emit('input', false)
        },
        createIssue: function() {
            console.log('created')
            this.emitClose()
        }
    }
}
</script>
