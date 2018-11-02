<template>
  <ul :class="ulClass">
    <li v-for="item in data" :class="liClass">{{ item }}</li>
  </ul>
</template>

<script>
export default {
    props: ['ulClass', 'liClass', 'data'],
}
</script>
