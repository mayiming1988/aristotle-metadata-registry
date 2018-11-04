<template>
  <div v-if="error.length > 0" class="alert alert-danger">{{ error }}</div>
</template>

<script>
export default {
    props: ['error']
}
</script>
