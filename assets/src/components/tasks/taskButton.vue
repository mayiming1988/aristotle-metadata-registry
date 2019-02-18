<template>
    <div>
    <button
        class="btn btn-primary task-btn"
        :disabled=isDisabled
        :ajaxurl=taskUrl
        @click="startTask"
        >{{ displayName }}</button>
    </div>
</template>

<script>
import apiRequest from 'src/mixins/apiRequest.js'

export default {
    mixins: [apiRequest],
    props: ['taskUrl', 'taskName', 'displayName', 'runningTasks'],
    data: () => ({
        isActive: true,
        processing: false,
        details: ""
    }),
    methods: {
        startTask: function() {
            let promise = this.get(this.taskUrl, {})
            this.processing = true
            this.details = "Processing..."
            promise.then((response) => {
                // this.processing = false
                this.details = "Done."

                if (response.status == 200 || response.status == 201) {
                    this.items = response.data.results
                }
                    //   setTimeout(this.status_update, 5000);
                this.$emit('new-task-started')
            })
        }
    },
    watch: {
        runningTasks: function (newer) {
            if (newer.includes(this.taskName)) {
                this.processing = true
            } else {
                this.processing = false
            }
        }
    },
    computed: {
        isDisabled() {
            return this.processing;
        }
    }
}
</script>

<style>
</style>
