import chai from 'chai'
import sinon from 'sinon'
import VueTestUtils from '@vue/test-utils'
import moment from 'moment'

var assert = chai.assert

import commentComponent from '../src/components/comment.vue'
import para from '../src/components/para.vue'

describe('comment', function() {

    beforeEach(function() {
        // Django style date
        this.datestring = '2018-11-09T04:17:48Z'

        this.wrapper = VueTestUtils.shallowMount(commentComponent, {
            propsData: {
                created: this.datestring
            }
        })

    })

    afterEach(function() {
        this.wrapper = {}
    })

    // Skipped until we can mock timezone
    it.skip('displays date correctly', function() {
        assert.equal(this.wrapper.vm.displayCreated, '9th Nov 2018, 05:17 PM')
    })

    it('sets paragraph text', function() {
        this.wrapper.setProps({
            created: this.datestring,
            body: 'Heck yeah'
        })
        return this.wrapper.vm.$nextTick().then(() => {
            assert.equal(this.wrapper.find('para-stub').props('text'), 'Heck yeah')
        })
    })

    it('renders name bold', function() {
        this.wrapper.setProps({
            created: this.datestring,
            name: 'Big name'
        })
        return this.wrapper.vm.$nextTick().then(() => {
            let strong = this.wrapper.find('strong')
            assert.equal(strong.text(), 'Big name')
        })
    })

    it('passes pic prop', function() {
        let fakepic = 'http://example.com/pic.jpg'
        this.wrapper.setProps({
            created: this.datestring,
            pic: fakepic
        })
        assert.equal(this.wrapper.find('user-panel-stub').props('pic'), fakepic)
    })
})
