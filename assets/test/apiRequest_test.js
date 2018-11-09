import chai from 'chai'
import sinon from 'sinon'
import VueTestUtils from '@vue/test-utils'

import apiRequest from '../src/mixins/apiRequest.js'
import switchEditApi from '../src/components/switchEditApi.vue'

var assert = chai.assert
var shallowMount = VueTestUtils.shallowMount
var mount = VueTestUtils.mount


describe('apiRequest', function() {

    beforeEach(function() {
        this.wrapper = shallowMount(apiRequest)
        this.server = sinon.createFakeServer({autoRespond: true})
        this.server.respondWith([
            200,
            {'Content-Type': 'application/json'},
            JSON.stringify({some: 'data'})
        ])
        document.cookie = 'csrftoken=faketoken'
    })

    afterEach(function() {
        this.server.restore()
        this.wrapper = {}
        document.cookie = ''
    })

    it('makes requests', function(done) {
        let promise = this.wrapper.vm.get('/fake/api/')

        promise.then(() => {
            assert.equal(this.server.requests.length, 1)
            let request = this.server.requests[0]
            assert.equal(request.method, 'GET')

            assert.deepEqual(this.wrapper.vm.response.data, {some: 'data'})
        })
        .then(done, done)
    })

    it('sets token header correctly', function(done) {
        let promise = this.wrapper.vm.get('/fake/api/')

        promise.then(() => {
            assert.equal(this.server.requests.length, 1)
            let request = this.server.requests[0]
            let headers = request.requestHeaders
            assert.equal(headers['X-CSRFToken'], 'faketoken')
        })
        .then(done, done)
    })
})
