<template>
  <modal :value="value" title="Create Issue" @input="emitClose">
    <issue-create></issue-create> 
  </modal>
</template>

<script>
import { Modal } from 'uiv'
import IssueCreate from '../components/issueCreate.vue'

export default {
    components: {
        Modal,
        IssueCreate
    },
    props: ['value'],
    methods: {
        emitClose: function() {
            this.$emit('input', false)
        }
    }
}
</script>
