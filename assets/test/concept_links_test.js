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
    })

    afterEach(function() {
        document.querySelector('a.aristotle-concept-link').remove()
    })

    function mouseOverElement(element) {
        let event = new Event('mouseover')
        element.dispatchEvent(event)
    }

    it('Loads tooltip on mouseover', function(done) {
        initConceptLinks()
        $(document).ready(() => {
            mouseOverElement(this.concept_link)
            assert.isTrue(this.concept_link.hasAttribute('aria-describedby'))
            let ttid = this.concept_link.getAttribute('aria-describedby')
            // Check tooltip exists
            assert.isNotNull(document.getElementById(ttid))
            done()
        })
    })
})
