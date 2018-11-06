<template>
    <div>
        <api-errors :errors="errors"></api-errors>
        <user-panel :pic="pic">
            <span slot="heading">
                New Comment
            </span>
            <textarea class="form-control" v-model="body"></textarea>
            <div class="panel-footer text-right" slot="footer">
                <button class="btn btn-primary" @click="makeComment">Comment</button>
            </div>
        </user-panel>
    </div>
</template>

<script>
import userPanel from './userPanel.vue'
import apiErrors from '../components/apiErrorDisplay.vue'
import apiRequest from '../mixins/apiRequest.js'

export default {
    mixins: [apiRequest],
    props: ['pic', 'userid', 'username', 'issueid', 'url'],
    components: {
        apiErrors,
        userPanel
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
                    let newcomment = {
                        'pic': this.pic,
                        'name': this.username,
                        'created': '2018',
                        'body': response.data['body']
                    }
                    this.$emit('created', newcomment)
                    this.body = ''
                }
            })
        }
    }
}
</script>

<style>
.text-right {
    text-align: "right"
}
</style>
