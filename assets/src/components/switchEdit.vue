<template>
  <div :id="divId">
    <div class="panel panel-default">
    <div class="panel-heading">
      <strong>{{ capitalName }}</strong>
      <a v-if="!editing && editable" class="inline-action pull-right" @click="toggleEdit">
        Edit <i class="fa fa-pencil" aria-hidden="true"></i>
      </a>
    </div>
    <div v-if="!editing" class="panel-body">
      <para :text="value"></para>
    </div>
    <div v-else class="panel-body">
      <div class="form-group">
        <api-errors :errors="errors"></api-errors>
        <textarea class="form-control" :name="name" v-model="value"></textarea>
      </div>
      <button class="btn btn-primary" type="submit" @click="submitInput">Save Changes</button>
      <button class="btn btn-default" type="submit" @click="toggleEdit">Cancel</button>
    </div>
    </div>
  </div>
</template>

<script>
import { getCSRF } from '../lib/cookie.js'
import { capitalize } from '../lib/utils.js'
import apiErrors from '../components/apiErrorDisplay.vue'
import para from '../components/para.vue'

export default {
    props: ['name', 'initial', 'submitUrl'], 
    components: {
        apiErrors,
        para
    },
    created: function() {
        this.value = this.initial
    },
    data: () => ({
        editing: false,
        value: '',
        errors: {}
    }),
    computed: {
        divId: function() {
            return 'switch-' + this.name
        },
        capitalName: function() {
            return capitalize(this.name)
        },
        editable: function() {
            return (this.submitUrl != undefined)
        }
    },
    methods: {
        toggleEdit: function() {
            this.editing = !this.editing
        },
        submitInput: function() {
            var component = this
            var data = {
                csrfmiddlewaretoken: getCSRF()
            }
            data[this.name] = this.value
            $.post(
                this.submitUrl,
                data,
                function(data) {
                    if (data.success) {
                        component.editing = false
                    } else {
                        component.errors = data.errors
                    }
                }
            )
        }
    }
}
</script>
