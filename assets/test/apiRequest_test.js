import chai from 'chai'
import sinon from 'sinon'
import VueTestUtils from '@vue/test-utils'

import apiRequest from '../src/mixins/apiRequest.js'

var assert = chai.assert
var shallowMount = VueTestUtils.shallowMount

function getSingleRequest(requestList) {
    assert.equal(requestList.length, 1)
    return requestList[0]
}

describe('apiRequest', function() {

    beforeEach(function() {
        this.wrapper = shallowMount(apiRequest)
        this.server = sinon.createFakeServer({respondImmediately: true})
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


    it('makes requests', function() {
        let promise = this.wrapper.vm.get('/fake/api/')

        return promise.then(() => {
            let request = getSingleRequest(this.server.requests)
            assert.equal(request.method, 'GET')

            assert.deepEqual(this.wrapper.vm.response.data, {some: 'data'})
        })
    })

    it('sets csrf token header', function() {
        let promise = this.wrapper.vm.get('/fake/api/')

        return promise.then(() => {
            let request = getSingleRequest(this.server.requests)
            let headers = request.requestHeaders
            assert.equal(headers['X-CSRFToken'], 'faketoken')
        })
    })


    it('posts data', function() {
        let promise = this.wrapper.vm.post('/fake/api/', {good: 'data'})

        return promise.then(() => {
            let request = getSingleRequest(this.server.requests)
            let body = JSON.parse(request.requestBody)
            assert.deepEqual(body, {good: 'data'})
        })
    })

    it('sets response on success', function() {
        let promise = this.wrapper.vm.get('/fake/api/')

        return promise.then((response) => {
            let request = getSingleRequest(this.server.requests)
            assert.equal(request.status, 200)
            assert.equal(this.wrapper.vm.response, response)
        })
    })

    it('sets errors and response on 400', function() {
        this.server.respondWith([
            400,
            {'Content-Type': 'application/json'},
            JSON.stringify({some: ['data']})
        ])
        let promise = this.wrapper.vm.get('/fake/api/')

        return promise.catch((error) => {
            let request = getSingleRequest(this.server.requests)
            assert.equal(request.status, 400)
            assert.equal(this.wrapper.vm.response, error.response)
            assert.deepEqual(this.wrapper.vm.errors, {some: ['data']})
        })
    })

    it('reports has errors properly', function() {
        assert.isFalse(this.wrapper.vm.hasErrors)
        this.wrapper.setData({errors: {some: 'errors'}})
        assert.isTrue(this.wrapper.vm.hasErrors)
    })

    it('reports has response properly', function() {
        assert.isFalse(this.wrapper.vm.hasResponse)
        this.wrapper.setData({response: {some: 'errors'}})
        assert.isTrue(this.wrapper.vm.hasResponse)
    })

})
