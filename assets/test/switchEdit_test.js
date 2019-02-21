import chai from 'chai'
import sinon from 'sinon'
import VueTestUtils from '@vue/test-utils'
import { clickElementIfExists, fakePromiseMethod } from './utils.js'

import switchEditComponent from '../src/components/switchEdit.vue'
import switchEditApi from '../src/components/switchEditApi.vue'

var assert = chai.assert
var shallowMount = VueTestUtils.shallowMount

describe('switchEditComponent', function() {

    beforeEach(function() {
        this.wrapper = shallowMount(switchEditComponent, {
            propsData: {
                name: 'description',
                initial: 'yay',
                submitUrl: '/test/'
            }
        })
    })

    it('displays correctly when not editing', function() {
        assert.equal(this.wrapper.find('para-stub').props('text'), 'yay')
        assert.equal(this.wrapper.find('a.inline-action').text(), 'Edit')
        assert.isFalse(this.wrapper.find('textarea').exists())
    })

    it('displays correctly when editing', function() {
        this.wrapper.setData({editing: true})
        return this.wrapper.vm.$nextTick().then(() => {
            assert.isTrue(this.wrapper.find('textarea').exists())
            assert.equal(this.wrapper.find('button.btn-primary').text(), 'Save Changes')
            assert.equal(this.wrapper.find('button.btn-default').text(), 'Cancel')
            assert.isFalse(this.wrapper.find('a.inline-action').exists())
        })
    })

    it('computes capital name', function() {
        assert.equal(this.wrapper.vm.capitalName, 'Description')
    })

    it('sets div id', function() {
        assert.equal(this.wrapper.vm.divId, 'switch-description')
        assert.equal(this.wrapper.attributes('id'), 'switch-description')
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
            value: 'Nice description',
            editing: true
        })

        return this.wrapper.vm.$nextTick().then(() => {
            clickElementIfExists(this.wrapper, 'button.btn-primary')

            assert.isTrue(fake.calledOnce)
            assert.isTrue(
                fake.calledWithExactly('/test/', {description: 'Nice description'})
            )
        })
    })

    it('sets editing false on success', function() {
        // setup fake patch method
        let fake = sinon.fake.resolves({status: 200})
        this.wrapper.setMethods({
            patch: fake
        })

        // Set data
        this.wrapper.setData({
            editing: true
        })

        return this.wrapper.vm.$nextTick().then(() => {
            clickElementIfExists(this.wrapper, 'button.btn-primary')

            assert.isTrue(fake.calledOnce)
            return this.wrapper.vm.$nextTick().then(() => {
                assert.isFalse(this.wrapper.vm.editing)
            })
        })
    })

    it('keeps editing true on fail', function() {
        // setup fake patch method
        let fake = sinon.fake.rejects()
        this.wrapper.setMethods({
            patch: fake
        })

        // Set data
        this.wrapper.setData({
            editing: true
        })

        return this.wrapper.vm.$nextTick().then(() => {
            clickElementIfExists(this.wrapper, 'button.btn-primary')

            assert.isTrue(fake.calledOnce)
            return this.wrapper.vm.$nextTick().then(() => {
                assert.isTrue(this.wrapper.vm.editing)
            })
        })
    })
})
