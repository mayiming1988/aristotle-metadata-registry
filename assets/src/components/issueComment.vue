<template>
    <div>
        <api-errors :errors="errors"></api-errors>
        <textarea v-model="body"></textarea>
        <button class="btn btn-primary" @click="makeComment">Comment</button>
    </div>
</template>

<script>
import apiErrors from '../components/apiErrorDisplay.vue'
import apiRequest from '../mixins/apiRequest.js'

export default {
    mixins: [apiRequest],
    props: ['userid', 'issueid', 'url'],
    components: {
        apiErrors
    },
    data: () => ({
        'body': ''
    }),
    methods: {
        makeComment: function() {
            let data = {
                'body': this.body,
                'author': this.userid,
                'issue': this.issueid
            }

            let promise = this.post(this.url, data)
            promise.then((response) => {
                // If comment created
                if (response.status == 201) {
                    this.$emit('created', response.data)
                }
            })
        }
    }
}
</script>
