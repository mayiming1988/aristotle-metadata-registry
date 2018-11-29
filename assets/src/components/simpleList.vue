<template>
  <ul :class="ulClass">
    <li v-for="item in data" :class="liClass">
        <slot :item="item">
            {{ item }}
        </slot>
    </li>
  </ul>
</template>

<script>
export default {
    props: ['ulClass', 'liClass', 'data'],
}
</script>
