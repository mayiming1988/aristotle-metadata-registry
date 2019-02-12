import chai from 'chai'
const assert = chai.assert
import VueTestUtils from '@vue/test-utils'

import editForm from '@/rules/editForm.vue'

describe('editForm', function() {

    beforeEach(function() {
        // Small schema used for testing
        this.schema = {
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
        // General wrapper
        this.wrapper = VueTestUtils.shallowMount(
            editForm,
            {propsData: {schema: JSON.stringify(this.schema), errors: {}}}
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
                    schema: JSON.stringify(this.schema), 
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
        assert.isTrue(this.wrapper.vm.submitted)
        // make change
        this.wrapper.setData({formData: {rules: 'name: new\nimportance: very'}})
        return this.wrapper.vm.$nextTick().then(() => {
            // check emit
            let edit_events = this.wrapper.emitted().edit
            assert.equal(edit_events.length, 1)
        })
    })

    it('doesnt emit edit made before submit', function() {
        // make change
        this.wrapper.setData({formData: {rules: 'name: new\nimportance: very'}})
        return this.wrapper.vm.$nextTick().then(() => {
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
        this.wrapper.setData({formData: {rules: 'name: new\nimportance: very'}})
        return this.wrapper.vm.$nextTick().then(() => {
            // check emit
            assert.equal(this.wrapper.emitted().edit.length, 1)
            // make second change
            this.wrapper.setData({formData: {rules: 'name: newer\nimportance: very'}})
            return this.wrapper.vm.$nextTick().then(() => {
                // make sure still 1 emit
                assert.equal(this.wrapper.emitted().edit.length, 1)
            })
        })
    })
})
