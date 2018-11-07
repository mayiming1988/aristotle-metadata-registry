<template>
  <user-panel :pic="pic">
    <template slot="heading">
      <strong>{{ name }}</strong>
      <span class="text-muted" :title="created">
        {{ created }}
      </span>
    </template>

    <template>
      <p v-for="line in bodyLines" class="small-p">{{ line }}</p>
    </template>
  </user-panel>
</template>

<script>
import userPanel from './userPanel.vue'
export default {
    props: ['pic', 'name', 'created', 'body'],
    components: {
      userPanel
    },
    computed: {
        bodyLines: function() {
            return this.body.split('\n')
        }
    }
}
</script>

<style>
.small-p {
    margin: 0
}
</style>
