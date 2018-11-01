import chai from 'chai'
import sinon from 'sinon'

const assert = chai.assert

import { initDAL } from '../src/lib/dal_simple_init.js'
import { initCKEditor } from '../src/lib/ckeditor_simple_init.js'

describe('DAL initializer', function() {

  beforeEach(() => {
    // Add select element to dom
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

describe('ckeditor initializer', function() {

  beforeEach(() => {
    // Add textarea to dom
    let textarea = document.createElement('textarea')
    textarea.setAttribute('id', 'id_important')
    textarea.setAttribute('data-type', 'ckeditortype')
    textarea.setAttribute('data-processed', 0)

    // Add options
    let options = { bodyClass: 'my_cke_class' }
    textarea.setAttribute('data-config', JSON.stringify(options))

    document.body.appendChild(textarea)
    //window.CKEDITOR_BASEPATH = '../node_modules/ckeditor/'
  })

  afterEach(() => {
    document.getElementById('id_important').remove()
  })

  it('initializes', () => {
    initCKEditor()
    let textarea = document.getElementById('id_important')
    assert.equal(textarea.getAttribute('data-processed'), 1)
  })

})
