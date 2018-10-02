import chai from 'chai'
import { addMessageRow } from './utils.js'

const assert = chai.assert

import { addHeaderMessage, initMessages } from '../src/lib/messages.js' 


describe('addHeaderMessage', function() {

  beforeEach(() => {
    addMessageRow(document.body)
  })

  afterEach(() => {
    document.getElementById('messages-row').remove()
  })

  it('adds a header message to the page', () => {
    addHeaderMessage('You have been informed')
    let ul = document.querySelector('ul.messages')
    assert.isNotNull(ul)
    let lis = ul.querySelectorAll('li')
    assert.equal(lis.length, 1)
    assert.equal(lis[0].textContent, 'You have been informed')
  })

  it('clears current messages, before adding', () => {
    addHeaderMessage('You have been informed')
    addHeaderMessage('You have been informed again')
    let ul = document.querySelector('ul.messages')
    assert.isNotNull(ul)
    let lis = ul.querySelectorAll('li')
    assert.equal(lis.length, 1)
    assert.equal(lis[0].textContent, 'You have been informed again')
  })

  it('remove hidden property', () => {
    let alert = document.querySelector('div.alert')
    assert.isNotNull(alert)
    assert.isTrue(alert.hasAttribute('hidden'))

    addHeaderMessage('You have been informed')

    assert.isFalse(alert.hasAttribute('hidden'))
  })

})
