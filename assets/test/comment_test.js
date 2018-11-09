import chai from 'chai'
import sinon from 'sinon'
import VueTestUtils from '@vue/test-utils'
import moment from 'moment'

var assert = chai.assert

import commentComponent from '../src/components/comment.vue'

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

    //it('displays date correctly', function() {
    //    assert.equal(this.wrapper.vm.displayCreated, '9th Nov 2018, 05:17 PM')
    //})
})
