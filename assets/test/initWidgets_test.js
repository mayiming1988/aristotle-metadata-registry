import chai from 'chai'
import sinon from 'sinon'

const assert = chai.assert

import { initDAL } from '../src/lib/dal_simple_init.js'

describe('DAL select box', function() {

  beforeEach(() => {
    let select = document.createElement('select')
    select.setAttribute('id', 'dal_selector')
    select.setAttribute('data-html', 'true')
    select.setAttribute('data-autocomplete-light-function', 'select2')
    select.setAttribute('data-autocomplete-light-url', '/givemedata')

    document.body.appendChild(select)

    this.server = sinon.createFakeServer()
  })

  afterEach(() => {
    document.getElementById('dal_selector').remove()
    this.server.restore()
  })

  it('initialises', () => {
    let select = document.getElementById('dal_selector')
    assert.notEqual(select.getAttribute('class'), 'select2-hidden-accessible')
    initDAL()
    assert.equal(select.getAttribute('class'), 'select2-hidden-accessible')
  })

  it('requests data when opened', () => {
    let select = $('#dal_selector')
    initDAL()

    assert.equal(this.server.requests.length, 0)
    select.select2('open')

    assert.equal(this.server.requests.length, 1)
    assert.equal(this.server.requests[0].url, '/givemedata')
  })

})
