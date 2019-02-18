import request from 'src/lib/request.js'

export default {
    data: () => ({
        request_error: '',
        // Wether to put request error in this.errors
        combine_errors: true,
        errors: {},
        loading: false,
        response: {}
    }),
    methods: {
        request: function(url, data, params, method) {
            this.loading = true
            let promise = request(method, url, data, params)

            promise.then((response) => {
                this.response = response
                this.loading = false
            })

            promise.catch((error) => {
                if (error.response) {
                    // Server responded with non 2xx status
                    let status_code = error.response.status
                    if (status_code == 400) {
                        this.errors = error.response.data
                    } else if (status_code >= 401 && status_code < 500) {
                        // Non validation 4xx status
                        this.setRequestError('Request could not be completed')
                    }

                    this.response = error.response
                } else if (error.request) {
                    // Request was sent, server did not respond
                    this.setRequestError('Request could not be completed. Please try again soon')
                } else {
                    // Request wasnt sent
                    this.setRequestError('Request could not be completed')
                }
                this.loading = false
            })
            // Return the promise so additional handlers can be added
            return promise
        },
        setRequestError: function(error_msg) {
            this.request_error = error_msg
            if (this.combine_errors) {
                this.errors = {'request': [error_msg]}
            }
        },
        post: function(url, data) {
            return this.request(url, data, {}, 'post')
        },
        get: function(url, params) {
            return this.request(url, {}, params, 'get')
        },
        patch: function(url, data) {
            return this.request(url, data, {}, 'patch')
        },
        put: function(url, data) {
            return this.request(url, data, {}, 'put')
        },
        delete: function(url, data) {
            return this.request(url, data, {}, 'delete')
        },
        isEmpty: function(obj) {
            return (Object.keys(obj).length == 0)
        },
        redirect: function(url) {
            window.location.assign(url)
        }
    },
    computed: {
        hasErrors: function() {
            return !this.isEmpty(this.errors)
        },
        hasResponse: function() {
            return !this.isEmpty(this.response)
        }
    }
}
