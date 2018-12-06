<template>
    <div class="single-error">
        <span v-if="hasBeError" class="text-danger">{{ beErrors[0] }}</span>
        <span v-if="!hasBeError && hasFeError" class="text-danger">{{ getErrorMsg(feErrors) }}</span>
    </div>
</template>

<script>
import getErrorMsg from 'src/lib/forms/getErrorMsg.js'

export default {
    props: {
        feErrors: {
            type: Object
        },
        beErrors: {
            type: Array
        }
    },
    computed: {
        hasFeError: function() {
            return (this.feErrors.$invalid)
        },
        hasBeError: function() {
            return (this.beErrors != undefined && this.beErrors.length > 0)
        }
    },
    methods: {
        getErrorMsg: getErrorMsg
    }
}
</script>
