import chai from 'chai'
const assert = chai.assert

import { buildElement } from 'src/lib/html.js'

describe('buildElement', function() {

    it('creates element', function() {
        let e = buildElement('a', {})
        assert.instanceOf(e, Element)
        assert.equal(e.tagName, 'A')
    })

    it('creates element with attrs', function() {
        let e = buildElement('a', {id: 1, class: 'link', customattr: 'Heck'})
        assert.equal(e.id, 1)
        assert.equal(e.className, 'link')
        assert.equal(e.getAttribute('customattr'), 'Heck')
    })

    it('creates element with text node', function() {
        let e = buildElement('a', {}, 'Some Text')
        assert.equal(e.textContent, 'Some Text')
    })

    it('creates element with attrs and text node', function() {
        let e = buildElement('a', {myattr: 'one'}, 'Some Text')
        assert.equal(e.getAttribute('myattr'), 'one')
        assert.equal(e.textContent, 'Some Text')
    })
})
