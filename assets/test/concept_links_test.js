import chai from 'chai'
import sinon from 'sinon'
const assert = chai.assert

import { initConceptLinks } from 'src/lib/concept_links.js'

describe('ConceptLinks', function() {

    beforeEach(function() {
        this.server = sinon.createFakeServer({respondImmediately: true})

        let link = document.createElement('a')
        link.className = 'aristotle-concept-link'
        link.href = '/item/7/'
        link.setAttribute('data-aristotle-concept-id', '7')
        link.appendChild(document.createTextNode('My Link'))

        this.concept_link = link
        document.querySelector('body').appendChild(this.concept_link)
    });

    afterEach(function() {
        document.querySelector('a.aristotle-concept-link').remove()
        this.server.restore()
    });

    function mouseOverElement(element) {
        let event = new Event('mouseover')
        element.dispatchEvent(event)
    }

    function respondWithDefn(server) {
        server.respondWith([
            200, 
            {'Content-Type': 'application/json'},
            JSON.stringify({short_definition: 'Yeah'})
        ])
    }

    it('Loads tooltip on mouseover', function(done) {
        initConceptLinks()
        $(document).ready(() => {
            assert.isFalse(this.concept_link.hasAttribute('aria-describedby'))
            mouseOverElement(this.concept_link)
            window.setTimeout( () => {
                assert.isTrue(this.concept_link.hasAttribute('aria-describedby'))
                let ttid = this.concept_link.getAttribute('aria-describedby')
                // Check tooltip exists
                assert.isNotNull(document.getElementById(ttid))
                done()
            }, 550)
        })
    })

    it('Makes api request on first hover', function(done) {
        respondWithDefn(this.server)
        initConceptLinks()
        $(document).ready(() => {
            mouseOverElement(this.concept_link)
            // Wait 550ms for request because of tooltip load delay
            window.setTimeout(() => {
                assert.equal(this.server.requests.length, 1)
                assert.equal(this.server.requests[0].url, '/api/v4/item/7')
                done()
            }, 550)
        })
    });

    it('Sets data-definition after request', function(done) {
        respondWithDefn(this.server)
        initConceptLinks()
        $(document).ready(() => {
            mouseOverElement(this.concept_link)
            assert.isNull(this.concept_link.getAttribute('data-definition'))
            // Wait 550ms for request
            window.setTimeout(() => {
                assert.equal(this.server.requests.length, 1)
                assert.equal(this.concept_link.getAttribute('data-definition'), 'Yeah')
                done()
            }, 550)
        })
    });

    it('Loads from data definition attr if available', function(done) {
        this.concept_link.setAttribute('data-definition', 'Wow');
        initConceptLinks();
        $(document).ready(() => {
            mouseOverElement(this.concept_link)
            window.setTimeout(() => {
                // Wait 550ms for request because of delay
                let ttid = this.concept_link.getAttribute('aria-describedby')
                assert.equal(document.getElementById(ttid).textContent, 'Wow')
                done()
            }, 550)
        })
    })
});
