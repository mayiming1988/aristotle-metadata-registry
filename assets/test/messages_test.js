import chai from 'chai'
import { addMessageRow, assertSingleMessage } from './utils.js'

const assert = chai.assert

import { addHeaderMessage, initMessages } from '../src/lib/messages.js' 


describe('addHeaderMessage', function() {

    beforeEach(function() {
        addMessageRow(document.body)
    })

    afterEach(function() {
        document.getElementById('messages-row').remove()
    })

    it('adds a header message to the page', function() {
        addHeaderMessage('You have been informed')
        assertSingleMessage('You have been informed')
    })

    it('clears current messages, before adding', function() {
        addHeaderMessage('You have been informed')
        addHeaderMessage('You have been informed again')
        assertSingleMessage('You have been informed again')
    })

    it('remove hidden property', function() {
        let alert = document.querySelector('div.alert')
        assert.isNotNull(alert)
        assert.isTrue(alert.hasAttribute('hidden'))

        addHeaderMessage('You have been informed')

        assert.isFalse(alert.hasAttribute('hidden'))
    })

})
