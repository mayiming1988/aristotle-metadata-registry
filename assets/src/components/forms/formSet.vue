<template>
    <div class="vue-formset">
        <Form 
            v-for="(item, index) in formsData" 
            :key="index" 
            :fields="fields" 
            :inline="true"
            :fieldPrefix="getPrefix(index)"
            :showSubmit="false">
        </Form>
        <button class="btn btn-success" @click="addRow">Add</button>
        <button class="btn btn-primary" @click="submitFormSet">Submit</button>
    </div>
</template>

<script>
import Form from '@/forms/form.vue'
export default {
    components: {
        Form
    },
    props: {
        fields: {
            type: Object
        },
        initial: {
            type: Array
        }
    },
    data: () => ({
        formsData: []
    }),
    created: function() {
        if (this.initial) {
            this.formsData = this.initial
        }
    },
    methods: {
        getPrefix: function(index) {
            return index.toString() + '-'
        },
        addRow: function() {
            this.formsData.push({})
        },
        submitFormSet: function() {
            return 0
        }
    }
}
</script>
