import chai from 'chai'
const assert = chai.assert
import VueTestUtils from '@vue/test-utils'

import editForm from '@/rules/editForm.vue'

describe('editForm', function() {

    beforeEach(function() {
        // Small schema used for testing
        let schema = {
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
        this.wrapper = VueTestUtils.shallowMount(
            editForm,
            {propsData: {schema: JSON.stringify(schema), errors: {}}}
        )
    })
    
    it('sets schema validation errors', function() {
        this.wrapper.setData({formData: {rules: 'name: wow'}})
        return this.wrapper.vm.$nextTick().then(() => {
            this.wrapper.vm.submit()
            assert.deepEqual(this.wrapper.vm.fe_errors['rules'], ['data should have required property \'importance\''])
        })
    })
})
