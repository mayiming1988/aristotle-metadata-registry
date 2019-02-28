import chai from 'chai'
import sinon from 'sinon'
import VueTestUtils from '@vue/test-utils'
import { assertSingleEmit, fakePromiseMethod, clickElementIfExists } from './utils.js'
var assert = chai.assert

import graphicalRepresentation from '../src/components/graphicalRepresentation.vue'

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