import chai from 'chai'
const assert = chai.assert
import VueTestUtils from '@vue/test-utils'

import baseForm from '@/forms/baseForm.vue'


describe('baseForm', function() {
     
    beforeEach(function() {
        this.wrapper = VueTestUtils.shallowMount(baseForm)
    })

    afterEach(function() {
        this.wrapper = {}
    })

    it('reports hasErrors true when there is a frontend error', function() {
        this.wrapper.setProps({fe_errors: {fieldname: {$invalid: true}}})
        assert.isTrue(this.wrapper.vm.hasErrors('fieldname'))
    })

    it('reports hasErrors true when there is a backend error', function() {
        this.wrapper.setProps({
            errors: {fieldname: ['Some errors']}, 
            fe_errors: {fieldname: {$invalid: false}}
        })
        assert.isTrue(this.wrapper.vm.hasErrors('fieldname'))
    })

    it('reports hasErrors false when no errors', function() {
        this.wrapper.setProps({
            fe_errors: {fieldname: {$invalid: false}},
            errors: {}
        })
        assert.isFalse(this.wrapper.vm.hasErrors('fieldname'))
    })

    it('returns labels as placeholders', function() {
        this.wrapper.setProps({
            fe_errors: {name: {$invalid: false}},
            inline: true,
            value: {},
            fields: {name: {label: 'TheName'}},
        })
        assert.equal(this.wrapper.vm.placeholder('name'), 'TheName')
    })

    it('returns capitalized names when no labels', function() {
        this.wrapper.setProps({
            fe_errors: {name: {$invalid: false}},
            inline: true,
            value: {},
            fields: {name: {}},
        })
        assert.equal(this.wrapper.vm.placeholder('name'), 'Name')
    })

    it('doesnt return placeholders if inline false', function() {
        this.wrapper.setProps({
            fe_errors: {name: {$invalid: false}},
            inline: false,
            value: {},
            fields: {name: {}},
        })
        assert.equal(this.wrapper.vm.placeholder('name'), '')
    })

})
