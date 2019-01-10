<template>
    <div class="download-component">
        <template v-if="!ready">
            <i class="fa fa-spinner fa-pulse"></i> Please wait while we are preparing your download
        </template>
        <template v-else>
            <alert v-if="error" type="danger">There was an error with your download. Please try again later</alert>
            <template v-else>
                <p>Your document is ready to download</p>
                <a class="btn btn-primary" :href="url">
                    <i class="fa fa-download"></i> Download now
                </a>
            </template>
        </template>
    </div>
</template>

<script>
import { Alert } from 'uiv'

export default {
    data: () => ({
        ready: false,
        error: false,
        pollTime: 1000, // period to call checkStatus in ms
        url: '#'
    }),
    components: {
        'alert': Alert
    },
    created: function() {
        this.interval = setInterval(this.checkStatus, this.pollTime)
    },
    beforeDestroy: function() {
        clearInterval(this.interval)
    },
    methods: {
        checkStatus: function() {
            $.getJSON('/dlstatus', (data) => {
                if (data.is_ready) {
                    this.ready = true
                    if (data.state != 'SUCCESS') {
                        this.error = true
                    } else if (data.result != undefined) {
                        this.url = data.result
                    }
                    clearInterval(this.interval)
                }
            })
        }
    }
}
</script>
