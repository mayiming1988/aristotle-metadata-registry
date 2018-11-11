import chai from 'chai'
import VueTestUtils from '@vue/test-utils'
import { assertSingleEmit } from './utils.js'

var assert = chai.assert

import issueComment from '../src/components/issueComment.vue'

describe('issueComment', function() {

    beforeEach(function() {
        this.wrapper = VueTestUtils.shallowMount(issueComment)
    })

    afterEach(function() {
        this.wrapper = {}
    })

    it('sets and emits isOpen on created', function() {
        assert.isFalse(this.wrapper.vm.isOpen)
        assertSingleEmit(this.wrapper, 'set_open', false)
    })

    it('sets and emits when isOpen is True', function() {
        this.wrapper = VueTestUtils.shallowMount(issueComment, {
            propsData: {
                issueIsOpen: 'True'
            }
        })
        assert.isTrue(this.wrapper.vm.isOpen)
        assertSingleEmit(this.wrapper, 'set_open', true)
    })

    it('sets can open close false', function() {
        this.wrapper.setProps({
            openClosePermission: 'False'
        })
        assert.isFalse(this.wrapper.vm.canOpenClose)
    })

    it('sets can open close true', function() {
        this.wrapper.setProps({
            openClosePermission: 'True'
        })
        assert.isTrue(this.wrapper.vm.canOpenClose)
    })

    it('sets open close text when open', function() {
        this.wrapper.setData({
            isOpen: true,
            body: ''
        })
        assert.equal(this.wrapper.vm.openCloseText, 'Close Issue')
        this.wrapper.setData({
            isOpen: true,
            body: 'some text'
        })
        assert.equal(this.wrapper.vm.openCloseText, 'Close and comment')
    })

    it('sets open close text when closed', function() {
        this.wrapper.setData({
            isOpen: false,
            body: ''
        })
        assert.equal(this.wrapper.vm.openCloseText, 'Reopen Issue')
        this.wrapper.setData({
            isOpen: false,
            body: 'some text'
        })
        assert.equal(this.wrapper.vm.openCloseText, 'Reopen and comment')
    })

    it('sets open close class when closed', function() {
        this.wrapper.setData({
            isOpen: false
        })
        assert.equal(this.wrapper.vm.openCloseClass, 'btn btn-success')
    })

    it('sets open close class when open', function() {
        this.wrapper.setData({
            isOpen: true
        })
        assert.equal(this.wrapper.vm.openCloseClass, 'btn btn-danger')
    })
})
