import chai from 'chai'
import VueTestUtils from '@vue/test-utils'

import switchEditComponent from '../src/components/switchEdit.vue'

var assert = chai.assert
var mount = VueTestUtils.mount
var shallowMount = VueTestUtils.shallowMount

describe('switchEditComponent', function() {

    var wrapper

    beforeEach(function() {
        wrapper = mount(switchEditComponent, {
            propsData: {
                name: 'description',
                initial: 'yay',
                submitUrl: '/test/'
            }
        })
    })

    it('displays correctly when not editing', function() {
        assert.include(wrapper.html(), '<p class="small-p">yay</p>')
        assert.include(wrapper.html(), 'Edit <i')
        assert.notInclude(wrapper.html(), '<textarea')
    })

    it('displays correctly when editing', function() {
        wrapper.setData({editing: true})
        assert.include(wrapper.html(), '<textarea')
        assert.include(wrapper.html(), 'Save Changes</button>')
        assert.include(wrapper.html(), 'Cancel</button>')
        assert.notInclude(wrapper.html(), 'Edit <i')
    })

    it('computes capital name', function() {
        assert.equal(wrapper.vm.capitalName, 'Description')
    })

    it('sets div id', function() {
        assert.equal(wrapper.vm.divId, 'switch-description')
        assert.include(wrapper.html(), '<div id="switch-description">')
    })
})
