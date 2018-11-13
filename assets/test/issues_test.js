import chai from 'chai'
import sinon from 'sinon'
import VueTestUtils from '@vue/test-utils'
import { assertSingleEmit, fakePromiseMethod, clickElementIfExists } from './utils.js'

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

    it('calls api request on button clicked', function() {
        // Setup fake post method
        let fake = fakePromiseMethod(this.wrapper, 'post')

        // Set props and data
        this.wrapper.setProps({
            commentUrl: '/fake/api/',
            userId: '7',
            issueId: '8',
        })
        this.wrapper.setData({
            body: 'Test body'
        })

        // Click comment button
        clickElementIfExists(this.wrapper, 'button.btn-primary')

        // Check calls
        assert.isTrue(fake.calledOnce)
        let call = fake.firstCall
        let expected_data = {
            body: 'Test body',
            author: '7',
            issue: '8'
        }
        assert.isTrue(call.calledWithExactly('/fake/api/', expected_data))
    })

    it('emitts created after comment created', function(done) {
        // Setup fake post method
        let fake = fakePromiseMethod(this.wrapper, 'post', {
            status: 201,
            data: {
                created: '2018',
                body: 'Test comment'
            }
        })

        // Set props
        this.wrapper.setProps({
            commentUrl: '/fake/api/',
            userId: '7',
            issueId: '8',
            userName: 'John',
            pic: 'example.com/pic.jpg'
        })

        // Click comment button
        clickElementIfExists(this.wrapper, 'button.btn-primary')

        // Check call and emit
        assert.isTrue(fake.calledOnce)
        let call = fake.firstCall
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

    it('calls post on open close, with no comment', function() {
        let fake = fakePromiseMethod(this.wrapper, 'post')

        // Set data and props
        this.wrapper.setProps({
            openCloseUrl: '/fake/api/',
            openClosePermission: 'True'
        })
        this.wrapper.setData({
            isOpen: false
        })
        
        clickElementIfExists(this.wrapper, 'button.btn-success')

        // Check called correctly
        assert.isTrue(fake.calledOnce)
        let call = fake.firstCall
        let expected = {
            isopen: true
        }
        assert.isTrue(call.calledWithExactly('/fake/api/', expected))
    })

    it('calls post on open close with comment', function() {
        let fake = fakePromiseMethod(this.wrapper, 'post')

        // Set data and props
        this.wrapper.setProps({
            openCloseUrl: '/fake/api/',
            openClosePermission: 'True'
        })
        this.wrapper.setData({
            isOpen: false,
            body: 'Some comment'
        })
        
        clickElementIfExists(this.wrapper, 'button.btn-success')

        // Check called correctly
        assert.isTrue(fake.calledOnce)
        let call = fake.firstCall
        let expected = {
            isopen: true,
            comment: {
                body: 'Some comment'
            }
        }
        assert.isTrue(call.calledWithExactly('/fake/api/', expected))
    })

    it('emits set_open when open changed', function(done) {
        let fake = fakePromiseMethod(this.wrapper, 'post', {
            status: 200,
            data: {
                issue: {
                    isopen: true
                }
            }
        })
        
        // Set data and props
        this.wrapper.setProps({
            openCloseUrl: '/fake/api/',
            openClosePermission: 'True'
        })
        this.wrapper.setData({
            isOpen: false,
        })

        clickElementIfExists(this.wrapper, 'button.btn-success')

        assert.isTrue(fake.calledOnce)
        fake.firstCall.returnValue.then(() => {
            assert.isTrue(this.wrapper.vm.isOpen)
            assert.isOk(this.wrapper.emitted('set_open'))
            assert.equal(this.wrapper.emitted('set_open').length, 2)
            assert.equal(this.wrapper.emitted('set_open')[1][0], true)
            assert.isNotOk(this.wrapper.emitted('created'))
        })
        .then(done, done)
    })

    it('emits created when open changed with comment', function(done) {
        let fake = fakePromiseMethod(this.wrapper, 'post', {
            status: 200,
            data: {
                issue: {
                    isopen: true
                },
                comment: {
                    body: 'Heck',
                    created: '2018'
                }
            }
        })
        
        // Set data and props
        this.wrapper.setProps({
            openCloseUrl: '/fake/api/',
            openClosePermission: 'True',
            pic: 'example.com/pic.jpg',
            userName: 'John'
        })
        this.wrapper.setData({
            isOpen: false,
        })

        clickElementIfExists(this.wrapper, 'button.btn-success')

        assert.isTrue(fake.calledOnce)
        fake.firstCall.returnValue.then(() => {
            assertSingleEmit(this.wrapper, 'created', {
                pic: 'example.com/pic.jpg',
                name: 'John',
                created: '2018',
                body: 'Heck'
            })
        })
        .then(done, done)
    })
})
