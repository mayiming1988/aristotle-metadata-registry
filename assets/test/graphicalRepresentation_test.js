import chai from 'chai'
import VueTestUtils from '@vue/test-utils'
var assert = chai.assert

import graphicalRepresentation from '../src/components/graphs/graphicalRepresentation.vue'

describe('graphicalRepresentation', function () {
    beforeEach(function () {
        this.wrapper = VueTestUtils.shallowMount(graphicalRepresentation)
    })

    afterEach(function () {
        this.wrapper = {}
    })

    it('sets and emits is ready to false on created', function () {
        assert.isFalse(this.wrapper.vm.ready)
        assert.isFalse(this.wrapper.vm.error)
    })

})
