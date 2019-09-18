import chai from 'chai'
const assert = chai.assert
import VueTestUtils from '@vue/test-utils'
import { fakePromiseMethod } from './utils.js'

import editForm from '@/rules/editForm.vue'
import RARulesEditor from '@/rules/RARulesEditor.vue'

// Small schema used for testing
var schema = {
    title: 'Bad Schema',
    type: 'object',
    properties: {
        name: {
            type: 'string'
        },
        importance: {
            type: 'string',
            enum: ['very', 'not much', 'not at all']
        }
    },
    required: ['name', 'importance']
}

describe('editForm', function() {

    beforeEach(function() {
        // General wrapper
        this.wrapper = VueTestUtils.shallowMount(
            editForm,
            {propsData: {schema: JSON.stringify(schema), errors: {}}}
        )
    })

    it('parses schema as json', function() {
        assert.isObject(this.wrapper.vm.schemaObj)
    })

    it('sets formdata from initial', function() {
        let initialData = {name: 'first', importance: 'very'}
        let newWrapper = VueTestUtils.shallowMount(
            editForm,
            {
                propsData: {
                    schema: JSON.stringify(schema), 
                    errors: {}, 
                    initial: initialData
                }
            }
        )
        assert.equal(newWrapper.vm.formData, initialData)
    })
    
    it('sets schema validation errors', function() {
        this.wrapper.setData({formData: {rules: 'name: wow'}})
        this.wrapper.vm.submit()
        assert.deepEqual(
            this.wrapper.vm.fe_errors['rules'], 
            ['data should have required property \'importance\'']
        )
    })

    it('emitts data when valid', function() {
        this.wrapper.setData({formData: {rules: 'name: wow\nimportance: very'}})
        this.wrapper.vm.submit()
        // Check submit was emitted once
        let submit_events = this.wrapper.emitted().submit
        assert.equal(submit_events.length, 1)
        assert.deepEqual(
            submit_events[0][0],
            {rules: 'name: wow\nimportance: very'}
        )
    })

    it('emits edit when edit made after submit', function() {
        // data so that submit will be successful
        this.wrapper.setData({formData: {rules: 'name: wow\nimportance: very'}})
        // submit
        this.wrapper.vm.submit()
        // make change
        assert.isTrue(this.wrapper.vm.submitted)
        this.wrapper.setData({formData: {rules: 'name: new\nimportance: very', submitted: true}})

        return this.wrapper.vm.$nextTick().then(() => {
            assert.isFalse(this.wrapper.vm.submitted)
            // check emit
            let edit_events = this.wrapper.emitted().edit
            assert.equal(edit_events.length, 1)
        })
    })

    it('doesnt emit edit made before submit', function() {
        // make change
        this.wrapper.setData({formData: {rules: 'name: new\nimportance: very'}})
        return this.wrapper.vm.$nextTick().then(() => {
            assert.isFalse(this.wrapper.vm.submitted)
            // check emit
            let edit_events = this.wrapper.emitted().edit
            assert.isNotOk(edit_events) // assert not truthy (will be undefined)
        })
    })

    it('only emits edit on first edit after submit', function() {
        // data so that submit will be successful
        this.wrapper.setData({formData: {rules: 'name: wow\nimportance: very'}})
        // submit
        this.wrapper.vm.submit()
        assert.isTrue(this.wrapper.vm.submitted)
        // make first change
        this.wrapper.setData({formData: {rules: 'name: new\nimportance: very', submitted: true}})
        return this.wrapper.vm.$nextTick().then(() => {
            // check emit
            assert.equal(this.wrapper.emitted().edit.length, 1)
            // make second change
            assert.isFalse(this.wrapper.vm.submitted)
            this.wrapper.setData({formData: {rules: 'name: newer\nimportance: very', submitted: false}})
            return this.wrapper.vm.$nextTick().then(() => {
                // make sure still 1 emit
                assert.equal(this.wrapper.emitted().edit.length, 1)
            })
        })
    })
})

describe('RARulesEditor', function() {

    beforeEach(function() {
        // General wrapper
        this.wrapper = VueTestUtils.shallowMount(
            RARulesEditor,
            {
                propsData: {
                    schema: JSON.stringify(schema), 
                    value: '',
                    api_url: '/fake/create',
                    method: 'post',
                    update_url_template: '/fake/update/{pk}/',
                    ra_id: 1
                }
            }
        )
    })
    
    function submitFakeData(wrapper, test_data, return_data) {
        let fake = fakePromiseMethod(wrapper, 'post', return_data)
        // Submit data
        wrapper.vm.submitData(test_data)
        // Make sure fake method was called
        assert.isTrue(fake.calledOnceWith('/fake/create', test_data))
    }

    it('sets submit url', function() {
        assert.equal(this.wrapper.vm.submit_url, '/fake/create')
    })

    it('sets submit method', function() {
        assert.equal(this.wrapper.vm.submit_method, 'post')
    })

    it('doesnt update url on non 201 status', function() {
        let test_data = {name: 'thing', importance: 'very'}
        submitFakeData(this.wrapper, test_data, {status: 500})
        // Make sure url & method not updated
        return this.wrapper.vm.$nextTick().then(() => {
            assert.equal(this.wrapper.vm.submit_url, '/fake/create')
            assert.equal(this.wrapper.vm.submit_method, 'post')
        })
    })

    it('switches to update url after create', function() {
        let test_data = {name: 'thing', importance: 'very'}
        submitFakeData(this.wrapper, test_data, {status: 201, data: {id: 5}})
        return this.wrapper.vm.$nextTick().then(() => {
            // Make sure url & method were updated
            assert.equal(this.wrapper.vm.submit_url, '/fake/update/5/')
            assert.equal(this.wrapper.vm.submit_method, 'put')
        })
    })
})
