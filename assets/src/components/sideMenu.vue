<template>
    <div class="list-group">
        <a v-for="(item, index) in items" 
            :key="item" 
            @click="clicked(index)" 
            :class="[{active: isActive(index)}, 'list-group-item', 'side-menu-item']"
            >
            {{ item }}
        </a>
    </div>
</template>

<script>
/* Github like side menu */
export default {
    props: {
        items: {
            type: Array,
            required: true
        },
        value: {
            type: Number,
            default: 0
        }
    },
    methods: {
        clicked: function(i) {
            this.$emit('input', i)
        },
        isActive: function(i) {
            return i == this.value
        }
    }
}
</script>

<style>
.side-menu-item {
    cursor: pointer
}
</style>
