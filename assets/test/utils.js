// Util functions used BY tests
import chai from 'chai'
import sinon from 'sinon'

const assert = chai.assert

export function addMessageRow(root_element) {
    var div = document.createElement("div")
    div.setAttribute('id', 'messages-row')
    div.setAttribute('class', 'row')

    var alert = document.createElement('div')
    alert.setAttribute('class', 'alert alert-info')
    alert.setAttribute('hidden', '')

    div.appendChild(alert)

    var ul = document.createElement('ul')
    ul.setAttribute('class', 'messages')

    alert.appendChild(ul)

    root_element.appendChild(div)
}

export function assertSingleMessage(message) {
    // Check that the message has been displayed
    let ul = document.querySelector('ul.messages')
    assert.isNotNull(ul)
    let lis = ul.querySelectorAll('li')
    assert.equal(lis.length, 1)
    assert.equal(lis[0].textContent, message)
}

export function assertSingleEmit(wrapper, event, value) {
    assert.isOk(wrapper.emitted(event))
    assert.equal(wrapper.emitted(event).length, 1)
    assert.deepEqual(wrapper.emitted(event)[0][0], value)
}

export function fakePromiseMethod(wrapper, method, return_value) {
    if (return_value == undefined) {
        return_value = {}
    }
    let fake = sinon.fake.resolves(return_value)
    wrapper.setMethods({
        [method]: fake
    })
    return fake
}

export function clickElementIfExists(wrapper, selector) {
    let element = wrapper.find(selector)
    assert.isTrue(element.exists())
    element.trigger('click')
}
