<template>
  <ul :class="ulClass">
    <li v-for="item in data" :key="item" :class="liClass">
        <slot :item="item">
            {{ item }}
        </slot>
    </li>
  </ul>
</template>

<script>
export default {
    props: {
        ulClass: {
            type: String,
            default: ''
        },
        liClass: {
            type: String,
            default: ''
        },
        data: {
            type: Array,
            required: true
        }
    }
}
</script>
