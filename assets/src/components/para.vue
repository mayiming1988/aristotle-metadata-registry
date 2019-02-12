<template>
  <div class="para-component">
    <p v-for="line in lines" :key="line" class="small-p">{{ line }}</p>
  </div>
</template>

<script>
export default {
    props: ['text'],
    computed: {
        lines: function() {
            return this.text.split('\n')
        }
    }
}
</script>

<style>
.small-p {
    margin: 0
}
</style>
