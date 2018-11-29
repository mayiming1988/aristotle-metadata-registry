<template>
    <div>
        <api-errors :errors="errors"></api-errors>
        <user-panel :pic="pic">
            <pre>{{ this.reviewState }}</pre>
            <span slot="heading">
                New Comment
            </span>
            <textarea class="form-control ta-fixed-width" v-model="body"></textarea>
            <div class="panel-footer text-right" slot="footer">
                <button v-if="canOpenCloseReview" :class="openCloseClass" @click="openClose">{{ openCloseText }}</button>
                <button class="btn btn-primary" @click="makeComment">Comment</button>
            </div>
        </user-panel>
    </div>
</template>

<script>
import userPanel from '@/userPanel.vue'
import apiErrors from '@/apiErrorDisplay.vue'
import apiRequest from 'src/mixins/apiRequest.js'

export default {
    mixins: [apiRequest],
    props: ['pic', 'userId', 'userName', 'reviewId', 'initialReviewState',
        'commentUrl', 'openCloseUrl', 'canOpenCloseReview'],
    components: {
        apiErrors,
        userPanel
    },
    data: () => ({
        body: '',
        reviewState: 'open',
        // isOpen: false
    }),
    created: function() {
        this.reviewState = this.initialReviewState
        this.$emit('set_status', this.reviewState)
    },
    methods: {
        emitComment: function(data) {
            let newcomment = {
                'pic': this.pic,
                'name': this.userName,
                'created': data['created'],
                'body': data['body']
            }
            this.$emit('created', newcomment)
        },
        makeComment: function() {
            let data = {
                'body': this.body,
                'author': this.userId,
                'request': this.reviewId
            }

            let promise = this.post(this.commentUrl, data)
            promise.then((response) => {
                // If comment created
                if (response.status == 201) {
                    this.emitComment(response.data)
                    this.body = ''
                }
            })
        },
        openClose: function() {
            let data = {
                // 'request': this.reviewId,
                'status': (this.isOpen ? "closed" : "open")
            }

            if (this.body.length > 0) {
                data['comment'] = {
                    'body': this.body
                }
            }

            let promise = this.patch(this.openCloseUrl, data)
            promise.then((response) => {
                // If success
                if (response.status == 200) {
                    if (response.data['comment'] != undefined) {
                        this.emitComment(response.data['comment'])
                    }
                    this.reviewState = response.data['status']
                    this.body = ''
                    this.$emit('set_status', response.data['status'])
                }
            })
        }
    },
    computed: {
        isOpen: function() {
            return this.reviewState == 'open'
        },
        canOpenClose: function() {
            return (this.openClosePermission == 'True')
        },
        openCloseText: function() {
            let text
            if (this.isOpen) {
                text = 'Close'
            } else {
                text = 'Reopen'
            }

            if (this.body.length > 0) {
                text += ' and comment'
            } else {
                text += ' Review'
            }
            return text
        },
        openCloseClass: function() {
            let base = 'btn btn-'
            if (this.isOpen) {
                return base + 'danger'
            } else {
                return base + 'success'
            }
        }
    }
}
</script>

<style>
.text-right {
    text-align: "right"
}
</style>
