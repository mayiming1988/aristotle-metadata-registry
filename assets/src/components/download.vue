<template>
    <div class="download-component">
        <template v-if="!ready">
            <i class="fa fa-spinner fa-pulse"></i> Please wait while we are preparing your download
        </template>
        <template v-else>
            <p>Your document is ready to download</p>
            <a class="btn btn-primary" :href="url">
                <i class="fa fa-download"></i> Download now
            </a>
        </template>
    </div>
</template>

<script>
export default {
    data: () => ({
        ready: false,
        pollTime: 1000, // period to call checkStatus in ms
        url: '#'
    }),
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
                    this.url = data.result
                    clearInterval(this.interval)
                }
            })
        }
    }
}
</script>
