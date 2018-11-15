<template>
  <div class="api-errors">
    <div v-for="(errlist, key) in errors" class="alert alert-danger" role="alert">
      <strong>{{ key }}:</strong>
      <ul v-if="errlist.length > 1">
        <li v-for="err in errlist">{{ err }}</li>
      </ul>
      <template v-else>{{ errlist[0] }}</template>
    </div>
  </div>
</template>

<script>
import { capitalize } from 'src/lib/utils.js'
export default {
    props: ['errors'],
    methods: {
        capitalize: capitalize
    }
}
</script>
