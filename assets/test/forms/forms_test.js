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
        this.wrapper.setProps({fe_errors: {fieldname: ['Error!']}})
        return this.wrapper.vm.$nextTick().then(() => {
            assert.isTrue(this.wrapper.vm.hasErrors('fieldname'))
        })
    })

    it('reports hasErrors true when there is a backend error', function() {
        this.wrapper.setProps({
            errors: {fieldname: ['Some errors']}, 
            fe_errors: {}
        })
        assert.isTrue(this.wrapper.vm.hasErrors('fieldname'))
    })

    it('reports hasErrors false when no errors', function() {
        this.wrapper.setProps({
            fe_errors: {},
            errors: {}
        })
        return this.wrapper.vm.$nextTick().then(() => {
            assert.isFalse(this.wrapper.vm.hasErrors('fieldname'))
        })
    })

    it('returns labels as placeholders', function() {
        this.wrapper.setProps({
            fe_errors: {},
            inline: true,
            value: {},
            fields: {name: {label: 'TheName'}},
        })
        assert.equal(this.wrapper.vm.placeholder('name'), 'TheName')
    })

    it('returns capitalized names when no labels', function() {
        this.wrapper.setProps({
            fe_errors: {},
            inline: true,
            value: {},
            fields: {name: {}},
        })
        assert.equal(this.wrapper.vm.placeholder('name'), 'Name')
    })

    it('doesnt return placeholders if inline false', function() {
        this.wrapper.setProps({
            fe_errors: {},
            inline: false,
            value: {},
            fields: {name: {}},
        })
        assert.equal(this.wrapper.vm.placeholder('name'), '')
    })

    it('doesnt pass backend errors if undefined', function() {
        assert.deepEqual(this.wrapper.vm.getBackendErrors('somefield'), [])
    })

    it('doesnt pass backend errors if blank', function() {
        this.wrapper.setProps({errors: {otherfields: ['Bad']}})
        return this.wrapper.vm.$nextTick().then(() => {
            assert.deepEqual(this.wrapper.vm.getBackendErrors('somefield'), undefined)
        })
    })

    it('passes backend errors when avaliable', function() {
        this.wrapper.setProps({errors: {somefield: ['Bad']}})
        return this.wrapper.vm.$nextTick().then(() => {
            assert.deepEqual(this.wrapper.vm.getBackendErrors('somefield'), ['Bad'])
        })
    })

    it('sets row class when inline', function() {
        this.wrapper.setProps({inline: true})
        return this.wrapper.vm.$nextTick().then(() => {
            assert.deepEqual(this.wrapper.classes(), ['vue-form', 'row'])
        })
    })

    it('doesnt set row class when non inline', function() {
        assert.deepEqual(this.wrapper.classes(), ['vue-form'])
    })

    it('passes data to formfield', function() {
        this.wrapper.setProps({
            fe_errors: {},
            value: {name: 'mydata'},
            fields: {name: {label: 'TheName', options: [], tag: 'input'}}
        })
        return this.wrapper.vm.$nextTick().then(() => {
            let ff = this.wrapper.find('formfield-stub')
            assert.equal(ff.props('tag'), 'input')
            assert.equal(ff.props('name'), 'name')
            assert.deepEqual(ff.props('options'), [])
            assert.equal(ff.props('value'), 'mydata')
        })
    })

    it('passes data to field wrapper', function() {
        this.wrapper.setProps({
            fe_errors: {},
            showLabels: false,
            inline: false,
            value: {name: 'mydata'},
            fields: {name: {label: 'TheName', options: [], tag: 'input'}},
        })
        return this.wrapper.vm.$nextTick().then(() => {
            let bfr = this.wrapper.find('bsfieldwrapper-stub')
            assert.equal(bfr.props('name'), 'name')
            assert.equal(bfr.props('label'), 'TheName')
            assert.equal(bfr.props('displayLabel'), false)
            assert.equal(bfr.props('column'), false)
            assert.equal(bfr.props('hasErrors'), false)
        })
    })

    it('emits data on input', function() {
        this.wrapper.setProps({
            fe_errors: {},
            value: {name: 'wow', desc: 'yeah'},
            fields: {name: {}, desc: {}}
        })
        return this.wrapper.vm.$nextTick().then(() => {
            this.wrapper.vm.fieldInput('name', 'wowee')
            assert.deepEqual(this.wrapper.emitted('input')[0][0], {name: 'wowee', desc: 'yeah'})
        })
    })


})
