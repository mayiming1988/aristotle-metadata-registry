<template>
    <div class="single-error">
        <span v-if="hasBeError" class="text-danger">{{ beErrors[0] }}</span>
        <span v-if="!hasBeError && hasFeError" class="text-danger">{{ feError }}</span>
    </div>
</template>

<script>
export default {
    props: {
        feError: {
            type: String
        },
        beErrors: {
            type: Array
        }
    },
    computed: {
        hasFeError: function() {
            return (this.feError != undefined)
        },
        hasBeError: function() {
            return (this.beErrors != undefined && this.beErrors.length > 0)
        }
    }
}
</script>
