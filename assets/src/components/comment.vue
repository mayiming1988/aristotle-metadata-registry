<template>
  <user-panel :pic="pic">
    <template slot="heading">
      <strong>{{ name }}</strong>
      <span class="text-muted" :title="created">
        {{ created }}
      </span>
    </template>

    <div class="panel-body">
      {{ body }}
    </div>
  </user-panel>
</template>

<script>
import userPanel from './userPanel.vue'
export default {
    props: ['pic', 'name', 'created', 'body'],
    components: {
      userPanel
    }
}
</script>
