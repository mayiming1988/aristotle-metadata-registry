<template>
  <div class="form-group">
    <label :for="name">{{ capitalize(name) }}</label>
    <slot></slot>
  </div>
</template>

<script>
import { capitalize } from 'src/lib/utils.js'

export default {
    props: ['name'],
    methods: {
        capitalize: capitalize
    }
}
</script>
