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
      {{ value }}
    </div>
    <div v-else class="panel-body">
      <div class="form-group">
        <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
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

export default {
    props: ['name', 'initial', 'submitUrl'], 
    created: function() {
        this.value = this.initial
    },
    data: () => ({
        editing: false,
        value: '',
        error: ''
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
                        if (data.errors[component.name] != undefined) {
                            component.error = data.errors[component.name]
                        } else {
                            component.error = 'Field could not be updated'
                        }
                    }
                }
            )
        }
    }
}
</script>
