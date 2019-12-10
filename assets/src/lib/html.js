// Utility functions for html interaction

// Build a html element with attributes and optional text node
export function buildElement(tagName, attrs, text) {
    let elem = document.createElement(tagName)
    for (let item of Object.entries(attrs)) {
        elem.setAttribute(item[0], item[1])
    }
    if (text) {
        elem.appendChild(document.createTextNode(text))
    }
    return elem
}

// Determine whether a form element is part of a formstage
export function isFormstageElement(element) {
    return element.id.includes('__prefix__')
}
