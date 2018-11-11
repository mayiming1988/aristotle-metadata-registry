import chai from 'chai'
import VueTestUtils from '@vue/test-utils'

import switchEditComponent from '../src/components/switchEdit.vue'

var assert = chai.assert
var shallowMount = VueTestUtils.shallowMount

describe('switchEditComponent', function() {

    var wrapper

    beforeEach(function() {
        wrapper = shallowMount(switchEditComponent, {
            propsData: {
                name: 'description',
                initial: 'yay',
                submitUrl: '/test/'
            }
        })
    })

    it('displays correctly when not editing', function() {
        assert.equal(wrapper.find('para-stub').props('text'), 'yay')
        assert.equal(wrapper.find('a.inline-action').text(), 'Edit')
        assert.isFalse(wrapper.find('textarea').exists())
    })

    it('displays correctly when editing', function() {
        wrapper.setData({editing: true})
        assert.isTrue(wrapper.find('textarea').exists())
        assert.equal(wrapper.find('button.btn-primary').text(), 'Save Changes')
        assert.equal(wrapper.find('button.btn-default').text(), 'Cancel')
        assert.isFalse(wrapper.find('a.inline-action').exists())
    })

    it('computes capital name', function() {
        assert.equal(wrapper.vm.capitalName, 'Description')
    })

    it('sets div id', function() {
        assert.equal(wrapper.vm.divId, 'switch-description')
        assert.equal(wrapper.attributes('id'), 'switch-description')
    })
})
