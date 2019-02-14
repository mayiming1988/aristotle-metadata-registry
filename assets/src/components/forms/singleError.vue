<template>
    <div class="single-error">
        <span v-if="hasBeError" class="text-danger">{{ beErrors[0] }}</span>
        <span v-if="!hasBeError && hasFeError" class="text-danger">{{ feErrors[0] }}</span>
    </div>
</template>

<script>
export default {
    props: {
        feErrors: {
            type: Array
        },
        beErrors: {
            type: Array
        }
    },
    computed: {
        hasFeError: function() {
            return (this.feErrors != undefined && this.feErrors.length > 0)
        },
        hasBeError: function() {
            return (this.beErrors != undefined && this.beErrors.length > 0)
        }
    },
}
</script>
