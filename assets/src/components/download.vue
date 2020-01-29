<template>
    <div class="download-component">
        <template v-if="!ready">
            <i class="fa fa-spinner fa-pulse"></i> Please wait while we are preparing your download
        </template>
        <template v-else>
            <alert v-if="error" type="danger">There was an error with your download. Please try again later</alert>
            <template v-else>
                <p>Your document is ready to download</p>
                <a class="btn btn-primary" :href="url" target="_blank" rel="noreferrer">
                    <i class="fa fa-external-link"></i> View download
                </a>
            </template>
        </template>
    </div>
</template>

<script>
import Alert from 'uiv/src/components/alert/Alert.vue'
import apiRequest from 'src/mixins/apiRequest.js'

export default {
    data: () => ({
        ready: false,
        error: false,
        pollTime: 1000, // period to call checkStatus in ms
        timeout: 30000, // peroid after which failure assumed if still pending
        url: '#'
    }),
    mixins: [apiRequest],
    components: {
        'alert': Alert
    },
    props: {
        status_url: String
    },
    created: function() {
        this.interval = setInterval(this.checkStatus, this.pollTime)
        this.pending = true
        this.started = Date.now()
    },
    beforeDestroy: function() {
        clearInterval(this.interval)
    },
    methods: {
        checkStatus: function() {
            this.get(this.status_url).then((response) => {
                let data = response.data
                if (data.state != 'PENDING') {
                    this.pending = false
                }
                if (data.is_ready) {
                    this.ready = true
                    // It is possible for the task to be done with state started for some reason
                    if (data.state != 'SUCCESS' && data.state != 'STARTED') {
                        this.error = true
                    } else if (data.result != undefined) {
                        this.url = data.result
                        document.title = "Download complete"
                    }
                    clearInterval(this.interval)
                }
            })
            // Check for timeout if we are still pending
            if (this.pending) {
                let time = Date.now()
                if ((time - this.started) > this.timeout) {
                    this.ready = true
                    this.error = true
                    clearInterval(this.interval)
                }
            }
        }
    }
}
</script>
