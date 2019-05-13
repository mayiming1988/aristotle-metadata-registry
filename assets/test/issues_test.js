import chai from 'chai'
import sinon from 'sinon'
import VueTestUtils from '@vue/test-utils'
import { assertSingleEmit, fakePromiseMethod, clickElementIfExists } from './utils.js'

var assert = chai.assert

import issueComment from '../src/components/issues/issueComment.vue'
import issueModal from '../src/components/issues/issueModal.vue'
import rootComponent from '../src/components/root/issues.js'

describe('issueComment', function() {

    beforeEach(function() {
        this.wrapper = VueTestUtils.mount(issueComment)
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
        return this.wrapper.vm.$nextTick().then(() => {
            assert.isTrue(this.wrapper.vm.canOpenClose)
            assert.equal(this.wrapper.vm.openCloseText, 'Reopen Issue')
            assert.equal(this.wrapper.find('button').text(), 'Reopen Issue')
        })
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

    it('emitts created after comment created', function() {
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
        return this.wrapper.vm.$nextTick().then(() => {
            assert.equal(this.wrapper.vm.body, '')
            assertSingleEmit(this.wrapper, 'created', {
                pic: 'example.com/pic.jpg',
                name: 'John',
                created: '2018',
                body: 'Test comment'
            })
        })
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
        
        return this.wrapper.vm.$nextTick().then(() => {
            clickElementIfExists(this.wrapper, 'button.btn-success')

            // Check called correctly
            assert.isTrue(fake.calledOnce)
            let call = fake.firstCall
            let expected = {
                isopen: true
            }
            assert.isTrue(call.calledWithExactly('/fake/api/', expected))
        })
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
        
        return this.wrapper.vm.$nextTick().then(() => {
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
    })

    it('emits set_open when open changed', function() {
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

        return this.wrapper.vm.$nextTick().then(() => {
            clickElementIfExists(this.wrapper, 'button.btn-success')

            assert.isTrue(fake.calledOnce)
            return this.wrapper.vm.$nextTick().then(() => {
                assert.isTrue(this.wrapper.vm.isOpen)
                assert.isOk(this.wrapper.emitted('set_open'))
                assert.equal(this.wrapper.emitted('set_open').length, 2)
                assert.isTrue(this.wrapper.emitted('set_open')[1][0])
                assert.isNotOk(this.wrapper.emitted('created'))
            })
        })
    })

    it('emits created when open changed with comment', function() {
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

        return this.wrapper.vm.$nextTick().then(() => {
            clickElementIfExists(this.wrapper, 'button.btn-success')

            assert.isTrue(fake.calledOnce)
            return this.wrapper.vm.$nextTick().then(() => {
                assertSingleEmit(this.wrapper, 'created', {
                    pic: 'example.com/pic.jpg',
                    name: 'John',
                    created: '2018',
                    body: 'Heck'
                })
                assert.equal(this.wrapper.vm.body, '')
            })
        })
    })

    it('updates body on textarea input', function() {
        assert.equal(this.wrapper.vm.body, '')
        this.wrapper.find('textarea').setValue('Comment body')
        assert.equal(this.wrapper.vm.body, 'Comment body')
    })
})

describe('issueModal', function() {

    beforeEach(function() {
        this.wrapper = VueTestUtils.shallowMount(issueModal)
    })

    afterEach(function() {
        this.wrapper = {}
    })

    it('updates formdata name input', function() {
        assert.equal(this.wrapper.vm.formdata.name, '')
        this.wrapper.find('input').setValue('Issue Name')
        assert.equal(this.wrapper.vm.formdata.name, 'Issue Name')
    })

    it('updates formdata description input', function() {
        assert.equal(this.wrapper.vm.formdata.description, '')
        this.wrapper.find('textarea').setValue('Issue Description')
        assert.equal(this.wrapper.vm.formdata.description, 'Issue Description')
    })

    it('emitts close when button clicked', function() {
        clickElementIfExists(this.wrapper, 'button.btn-default')
        assertSingleEmit(this.wrapper, 'input', false)
    })

    it('calls post on create issue click', function() {
        this.wrapper.setProps({
            iid: '1',
            url: '/fake/api/'
        })
        this.wrapper.setData({
            formdata: {name: 'Test Name', description: 'Test Desc'}
        })
        let fake = fakePromiseMethod(this.wrapper, 'post', {})
        clickElementIfExists(this.wrapper, 'button.btn-primary')

        assert.isTrue(fake.calledOnce)
        let expected_data = {
            name: 'Test Name',
            description: 'Test Desc',
            item: '1'
        }
        assert.isTrue(fake.calledWithExactly('/fake/api/', expected_data))
    })

    it('redirects on 201 response with url', function() {
        let fake = fakePromiseMethod(this.wrapper, 'post', {
            status: 201,
            data: {
                url: 'some/fake/url/'
            }
        })
        let fakeRedi = sinon.fake()
        this.wrapper.setMethods({
            redirect: fakeRedi
        })

        clickElementIfExists(this.wrapper, 'button.btn-primary')

        assert.isTrue(fake.calledOnce)
        return this.wrapper.vm.$nextTick().then(() => {
            assert.isTrue(fakeRedi.calledOnce)
            assert.isTrue(fakeRedi.calledWithExactly('some/fake/url/'))
        })
    })

    it('doesn\'t redirect on non 201 status', function() {
        let fake = fakePromiseMethod(this.wrapper, 'post', {
            status: 999,
            data: {
                url: 'some/fake/url/'
            }
        })
        let fakeRedi = sinon.fake()
        this.wrapper.setMethods({
            redirect: fakeRedi
        })

        clickElementIfExists(this.wrapper, 'button.btn-primary')

        assert.isTrue(fake.calledOnce)
        return this.wrapper.vm.$nextTick().then(() => {
            assert.isFalse(fakeRedi.called)
        })
    })
})

describe('issueRootComponent', function() {

    beforeEach(function() {
        // convert root component data to function
        let initData = rootComponent.data
        this.wrapper = VueTestUtils.shallowMount(rootComponent, {
            data: () => (initData)
        })
    })

    afterEach(function() {
        this.wrapper = {}
    })

    it('sets is open correctly', function() {
        assert.isTrue(this.wrapper.vm.isOpen)
        this.wrapper.vm.setIsOpen(false)
        assert.isFalse(this.wrapper.vm.isOpen)
    })

    it('adds comment correctly', function() {
        assert.isEmpty(this.wrapper.vm.new_comments)
        this.wrapper.vm.addComment({body: 'yeah'})
        this.wrapper.vm.addComment({body: 'wow'})
        let expected = [{body: 'yeah'}, {body: 'wow'}]
        assert.deepEqual(this.wrapper.vm.new_comments, expected)
    })
})
