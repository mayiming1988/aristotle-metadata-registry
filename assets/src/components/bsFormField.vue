<template>
  <div class="form-group">
    <label :for="name">{{ capitalize(name) }}</label>
    <slot :id="name"></slot>
  </div>
</template>

<script>
import { capitalize } from '../lib/utils.js'
export default {
    props: ['name'],
    methods: {
        capitalize: capitalize
    }
}
</script>
