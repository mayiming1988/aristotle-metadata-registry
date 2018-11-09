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
        document.cookie = 'csrftoken=faketoken'
    })

    afterEach(function() {
        this.server.restore()
        this.wrapper = {}
        document.cookie = ''
    })

    it('makes get request', function(done) {
        this.server.respondWith([
            200,
            {'Content-Type': 'application/json'},
            JSON.stringify({some: 'data'})
        ])
        let promise = this.wrapper.vm.get('/fake/api/')

        promise.then((response) => {
            console.log('we in')
            assert.equal(this.server.requests.length, 1)
            let request = this.server.requests[0]
            assert.equal(request.method, 'GET')

            assert.deepEqual(this.wrapper.vm.response.data, {some: 'data'})
            done()
        })
    })
})
