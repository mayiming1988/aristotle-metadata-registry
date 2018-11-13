import chai from 'chai'
import sinon from 'sinon'
import VueTestUtils from '@vue/test-utils'
import { clickElementIfExists, fakePromiseMethod } from './utils.js'

import switchEditComponent from '../src/components/switchEdit.vue'
import switchEditApi from '../src/components/switchEditApi.vue'

var assert = chai.assert
var shallowMount = VueTestUtils.shallowMount

describe('switchEditComponent', function() {

    var wrapper

    beforeEach(function() {
        wrapper = shallowMount(switchEditComponent, {
            propsData: {
                name: 'description',
                initial: 'yay',
                submitUrl: '/test/'
            }
        })
    })

    it('displays correctly when not editing', function() {
        assert.equal(wrapper.find('para-stub').props('text'), 'yay')
        assert.equal(wrapper.find('a.inline-action').text(), 'Edit')
        assert.isFalse(wrapper.find('textarea').exists())
    })

    it('displays correctly when editing', function() {
        wrapper.setData({editing: true})
        assert.isTrue(wrapper.find('textarea').exists())
        assert.equal(wrapper.find('button.btn-primary').text(), 'Save Changes')
        assert.equal(wrapper.find('button.btn-default').text(), 'Cancel')
        assert.isFalse(wrapper.find('a.inline-action').exists())
    })

    it('computes capital name', function() {
        assert.equal(wrapper.vm.capitalName, 'Description')
    })

    it('sets div id', function() {
        assert.equal(wrapper.vm.divId, 'switch-description')
        assert.equal(wrapper.attributes('id'), 'switch-description')
    })
})


describe('switchEditApi', function() {

    beforeEach(function() {
        this.wrapper = shallowMount(switchEditApi, {
            propsData: {
                name: 'description',
                initial: 'yay',
                submitUrl: '/test/'
            }
        })
    })

    it('makes patch request on submit', function() {
        let fake = fakePromiseMethod(this.wrapper, 'patch', {})

        this.wrapper.setData({
            value: 'Nice description'
        })
        clickElementIfExists(this.wrapper, 'button.btn-primary')

        assert.isTrue(fake.calledOnce)
        assert.isTrue(
            fake.calledWithExactly('/test/', {description: 'Nice description'})
        )
    })

    it('sets editing false on success', function(done) {
        // setup fake patch method
        let fake = sinon.fake.resolves({status: 200})
        this.wrapper.setMethods({
            patch: fake
        })

        // Set data
        this.wrapper.setData({
            editing: true
        })

        clickElementIfExists(this.wrapper, 'button.btn-primary')

        assert.isTrue(fake.calledOnce)
        fake.firstCall.returnValue.then(() => {
            assert.isFalse(this.wrapper.vm.editing)
        })
        .then(done, done)
    })
})
