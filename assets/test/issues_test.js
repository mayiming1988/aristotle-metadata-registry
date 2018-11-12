import chai from 'chai'
import sinon from 'sinon'
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

    it('doesnt render button if no open close permission', function() {
        assert.isFalse(this.wrapper.vm.canOpenClose)
        assert.equal(this.wrapper.vm.openCloseText, 'Reopen Issue')
        assert.notEqual(this.wrapper.find('button').text(), 'Reopen Issue')
    })

    it('renders button if open close permission', function() {
        this.wrapper.setProps({
            openClosePermission: 'True'
        })
        assert.isTrue(this.wrapper.vm.canOpenClose)
        assert.equal(this.wrapper.vm.openCloseText, 'Reopen Issue')
        assert.equal(this.wrapper.find('button').text(), 'Reopen Issue')
    })

    it('creates comment when button clicked', function(done) {
        // Setup fake post method
        let fakeresponse = {
            status: 201,
            data: {
                created: '2018',
                body: 'Test comment'
            }
        }
        let fakepost = sinon.fake.resolves(fakeresponse)
        this.wrapper.setMethods({
            post: fakepost
        })

        // Set props and data
        this.wrapper.setProps({
            commentUrl: '/fake/api/',
            userId: '7',
            issueId: '8',
            pic: 'example.com/pic.jpg',
            userName: 'John'
        })
        this.wrapper.setData({
            body: 'Test body'
        })

        // Get comment button
        let commentButton = this.wrapper.find('button.btn-primary')
        assert.isTrue(commentButton.exists())
        
        // Click comment button
        commentButton.trigger('click')

        // Check calls and emmits
        assert.isTrue(fakepost.calledOnce)
        let call = fakepost.firstCall
        let expected_data = {
            body: 'Test body',
            author: '7',
            issue: '8'
        }
        assert.isTrue(call.calledWithExactly('/fake/api/', expected_data))
        call.returnValue.then(() => {
            assert.equal(this.wrapper.vm.body, '')
            assertSingleEmit(this.wrapper, 'created', {
                pic: 'example.com/pic.jpg',
                name: 'John',
                created: '2018',
                body: 'Test comment'
            })
        })
        .then(done, done)
    })
})
