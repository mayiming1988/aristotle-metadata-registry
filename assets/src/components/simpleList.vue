<template>
  <ul :class="ulClass">
    <li v-for="item in data" :key="getKey(item)" :class="liClass">
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
    },
    methods: {
        getKey: function(item) {
            // If we got an object with an id use that
            if (typeof item == "object" && item.id !== undefined) {
                return item.id
            }
            // Fallback to item
            return item
        }
    }
}
</script>
