import chai from 'chai'
import VueTestUtils from '@vue/test-utils'
const assert = chai.assert

import { fakePromiseMethod } from './utils.js'
import inlineEdit from '@/inlineEdit.vue'

describe('inlineEdit', function() {

    beforeEach(function() {
        this.wrapper = VueTestUtils.shallowMount(inlineEdit)
    })

    it('Switches to edit on click', function() {
        assert.isFalse(this.wrapper.vm.editing)
        this.wrapper.find('button').trigger('click')
        assert.isTrue(this.wrapper.vm.editing)
    })

    it('Sitches back on cancel', function() {
        this.wrapper.setData({editing: true})
        this.wrapper.find('button.btn-default').trigger('click')
        assert.isFalse(this.wrapper.vm.editing)
    })

    it('updates value from input', function() {
        this.wrapper.setData({editing: true})
        return this.wrapper.vm.$nextTick().then(() => {
            this.wrapper.find('input').setValue('My Desc')
            assert.equal(this.wrapper.vm.value, 'My Desc')
        })
    })

    it('submits value on save', function() {
        this.wrapper.setProps({submitUrl: '/api/thing', fieldName: 'description'})
        this.wrapper.setData({editing: true, value: 'My Desc'})
        let fake = fakePromiseMethod(this.wrapper, 'patch')

        this.wrapper.find('button.btn-primary').trigger('click')
        assert.isTrue(fake.calledWithExactly('/api/thing', {description: 'My Desc'}))
    })

    it('displays errors', function() {
        this.wrapper.setData({editing: true, errors: {field: ['Big error']}})
        return this.wrapper.vm.$nextTick().then(() => {
            let errorstub = this.wrapper.find('api-errors-stub')
            assert.deepEqual(errorstub.props('errors'), {field: ['Big error']})
        })
    })
})
