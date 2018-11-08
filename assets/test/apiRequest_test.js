import chai from 'chai'
import sinon from 'sinon'
import VueTestUtils from '@vue/test-utils'

import { apiRequest } from '../src/mixins/apiRequest.js'
import switchEditApi from '../src/components/switchEditApi.vue'

var assert = chai.assert
var shallowMount = VueTestUtils.shallowMount
var mount = VueTestUtils.mount


describe('apiRequest', function() {


    beforeEach(function() {
        var testApiComponent = {
            template: '<div>hello<\/div>',
            mixins: [apiRequest]
        }
        let wrapper = shallowMount(testApiComponent, {})

        this.server = sinon.createFakeServer()
    })

    afterEach(function() {
        this.server.restore()
    })

    it('makes get request', function() {
        wrapper.vm.get('/fake/api/')
        this.server.respond()

        assert.equal(this.server.requests.length, 1)
    })
})
