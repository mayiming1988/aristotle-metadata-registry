<template>
    <span>
    <button @click="refresh" class="btn btn-primary">Refresh</button>
    <span>{{ details }}</span>
    </span>
</template>

<script>
import apiRequest from 'src/mixins/apiRequest.js'

export default {
    mixins: [apiRequest],
    props: [],
    data: () => ({
        isActive: true,
        processing: false,
        details: ""
    }),
    created: function() {
    },
    methods: {
        refresh: function() {
            this.$emit('refresh-tasks')
        }
    },
    computed: {
    }
}
</script>

<style>
</style>
