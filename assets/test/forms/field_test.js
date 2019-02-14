import chai from 'chai'
const assert = chai.assert
import VueTestUtils from '@vue/test-utils'

import field from '@/forms/formField.vue'


describe('formField', function() {

    beforeEach(function() {
        this.wrapper = VueTestUtils.shallowMount(field)
    })

    afterEach(function() {
        this.wrapper = {}
    })

    it('passes data to component', function() {
        this.wrapper.setProps({
            tag: 'input',
            name: 'description',
            value: 'the best the best the best the best the best the best',
            fieldClass: 'myClass',
        })

        return this.wrapper.vm.$nextTick().then(() => {
            let input = this.wrapper.find('input')
            assert.equal(input.props('name'), 'description')
            assert.deepEqual(input.classes(), ['myClass'])
            assert.equal(input.props('value'), 'the best the best the best the best the best the best')
        })
    })

    it('set hasOptions false when no options', function() {
        assert.isFalse(this.wrapper.vm.hasOptions())
    })

    it('set hasOptions true when there are options', function() {
        this.wrapper.setProps({
            options: ['lit', 'fam']
        })
        assert.isFalse(this.wrapper.vm.hasOptions())
    })

    it('emitts value', function() {
        this.wrapper.setProps({
            name: 'description',
            value: 'wow'
        })
        this.wrapper.find('input').setValue('fancy')
        assert.isOk(this.wrapper.emitted('input'))
        assert.equal(this.wrapper.emitted('input').length, 1)
        assert.equal(this.wrapper.emitted('input')[0][0], 'fancy')
    })

    it('displays options', function() {
        this.wrapper.setProps({
            tag: 'select',
            name: 'animal',
            options: [['d', 'dog'], ['c', 'cat']],
            value: 'c'
        })
        return this.wrapper.vm.$nextTick().then(() => {
            // Check 2 options are present
            assert.equal(this.wrapper.findAll('option').length, 2)
            assert.isTrue(this.wrapper.find('option[value=c]').exists())
            assert.isTrue(this.wrapper.find('option[value=d]').exists())
        })
    })
})
