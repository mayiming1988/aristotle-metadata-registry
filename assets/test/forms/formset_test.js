import chai from 'chai'
const assert = chai.assert
import VueTestUtils from '@vue/test-utils'


import Formset from '@/forms/formSet.vue'

describe('FormSet', function() {

    beforeEach(function() {
        // this.wrapper = VueTestUtils.shallowMount(Formset)
    })

    afterEach(function() {
        this.wrapper = {}
    })

    it('Sets data to initial', function() {
        let propsData = {
            fields: {name: {tag: 'input', rules: {required: false}}},
            initial: [{name: 'Heck'}, {name: 'Flip'}]
        }
        let wrapper = VueTestUtils.shallowMount(Formset, {propsData: propsData})

        let expectedData = [
            {name: 'Heck', vid: 0, new: false}, 
            {name: 'Flip', vid: 1, new: false}
        ]
        assert.deepEqual(wrapper.vm.formsData, expectedData)
    })
})
